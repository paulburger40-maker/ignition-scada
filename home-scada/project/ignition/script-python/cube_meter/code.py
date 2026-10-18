"""Read-only CUBE API client for one positively identified household meter."""
import json,math,threading,time,sys

DEVICE_ID='10023339b5'
# Observed in CUBE's built-in integration and cross-checked with its synced-device page.
BUILTIN_DEVICE_ID=DEVICE_ID+'_built_in'
BASE='http://127.0.0.1:18090/open-api/v2/rest/'
SECRET_FILE='C:/Users/Paul/IgnitionHome/private/cube-api-secret.json'
GLOBAL_KEY='home_scada_cube_meter_readonly_v1'
_lock=threading.RLock()
_worker_id=object()
_client=None

def _failure(stage):
    kind=getattr(sys.exc_info()[0],'__name__','NativeError')
    _shared()['status']='Meter connection failed at '+stage+' ('+kind+'). Check Gateway diagnostics.'
    system.util.getLogger('HomeSCADA.Meter').warn('Meter reader failure stage='+stage+' kind='+kind)

def _has_id(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if str(key).lower().replace('_','') in ('deviceid','ewelinkdeviceid','ewelinkid') and str(item)==DEVICE_ID:
                return True
            if isinstance(item,(dict,list)) and _has_id(item): return True
    elif isinstance(value,list):
        return any(_has_id(item) for item in value)
    return False

def select_meter(payload):
    if not isinstance(payload,dict) or payload.get('error')!=0:
        raise ValueError('CUBE response was not successful')
    devices=payload.get('data',{}).get('device_list',[])
    matches=[d for d in devices if isinstance(d,dict) and
             (str(d.get('serial_number',''))==DEVICE_ID or
              str(d.get('third_serial_number','')) in (DEVICE_ID,BUILTIN_DEVICE_ID) or _has_id(d.get('tags',{})))]
    if len(matches)!=1: raise ValueError('Exactly one matching POWCT device is required')
    return matches[0]

def decode_meter(device):
    result=dict(device_id=DEVICE_ID,online=False,status='Meter offline or online state unavailable',
                power_w=None,power_kw=None,voltage_v=None,current_a=None,
                firmware=str(device.get('firmware_version','Unreported')),
                today_kwh=None,month_kwh=None,total_kwh=None,physical_commands_enabled=False)
    if device.get('online') is not True: return result
    state=device.get('state',{})
    capabilities=set(c.get('capability') for c in device.get('capabilities',[]) if isinstance(c,dict))
    for capability,target in [('electric-power','power_w'),('voltage','voltage_v'),('electric-current','current_a')]:
        if capability not in capabilities: continue
        block=state.get(capability,{})
        raw=block.get(capability) if isinstance(block,dict) else None
        if raw is None: continue
        if isinstance(raw,bool): raise ValueError('Boolean is not an electrical measurement')
        value=float(raw)
        if math.isnan(value) or math.isinf(value) or value<0:
            raise ValueError('Invalid or unsupported electrical measurement')
        # Official generic CUBE V2 capability units: 0.01 W, V and A.
        result[target]=value/100.0
    if result['power_w'] is None:
        result['status']='Online; electrical capability mapping not yet available'
        return result
    result.update(online=True,status='Live reading candidate - validate against eWeLink',power_kw=result['power_w']/1000.0)
    # Daily/monthly counters and lifetime totals are deliberately not guessed.
    return result

def _shared():
    values=system.util.getGlobals()
    with _lock:
        if GLOBAL_KEY not in values:
            values[GLOBAL_KEY]=dict(owner=None,updated_ms=0,status='Bridge authorization needed',online=False,
                power_w=None,power_kw=None,voltage_v=None,current_a=None,today_kwh=None,month_kwh=None,
                total_kwh=None,firmware='Unreported',device_id=DEVICE_ID,physical_commands_enabled=False)
        return values[GLOBAL_KEY]

def _get(endpoint,token=None):
    global _client
    if endpoint not in ('bridge/access_token','devices'):
        raise ValueError('Read-only endpoint not allowed')
    headers={'Accept':'application/json','Content-Type':'application/json'}
    if token: headers['Authorization']='Bearer '+token
    with _lock:
        if _client is None:
            _client=system.net.httpClient(timeout=3000,version='HTTP_1_1',redirect_policy='NEVER',cookie_policy='ACCEPT_NONE')
        client=_client
    params={'app_name':'Ignition Home SCADA'} if endpoint=='bridge/access_token' else None
    response=client.get(BASE+endpoint,headers=headers,params=params,timeout=3000)
    accepted=(200,400,401) if endpoint=='bridge/access_token' else (200,)
    if response.statusCode not in accepted: raise RuntimeError('CUBE HTTP request failed')
    return response.json

def authorize(session_id):
    shared=_shared()
    stage='administrator check'
    try:
        if not session_id or not system.perspective.isAuthorized(False,['Authenticated/Roles/Administrator'],session_id):
            shared['status']='Administrator access is required to authorize the meter bridge'
            return False
        shared['last_action_ms']=system.date.toMillis(system.date.now())
        stage='bridge API request'
        payload=_get('bridge/access_token')
        if payload.get('error')!=0:
            if payload.get('error')!=401:
                shared['status']='Bridge rejected the authorization request (code '+str(payload.get('error'))+'). Gateway configuration needs inspection.'
                return False
            shared['status']='Approve the API-access popup in CUBE. Waiting up to two minutes for approval.'
            shared['authorize_until']=time.time()+120
            _start()
            return False
        stage='credential encryption and storage'
        _store_credential(payload)
        shared['status']='Bridge authorized; waiting for matching meter readings'
        _start()
        return True
    except:
        _failure(stage)
        return False

def _store_credential(payload):
    token=payload.get('data',{}).get('token')
    if not isinstance(token,basestring) or not 16<=len(token)<=2048:
        raise ValueError('Unexpected API credential')
    cipher=system.secrets.encrypt(token)
    if not cipher: raise RuntimeError('Secret encryption failed')
    system.file.writeFile(SECRET_FILE,system.util.jsonEncode(cipher))
    _shared()['authorize_until']=0

def _run():
    shared=_shared()
    while shared.get('owner') is _worker_id:
        stage='credential decryption'
        try:
            if not system.file.fileExists(SECRET_FILE):
                if time.time()>shared.get('authorize_until',0):
                    shared['status']='Bridge approval timed out. Click Connect meter to request again.'
                    shared['owner']=None
                    return
                stage='API consent polling'
                payload=_get('bridge/access_token')
                if payload.get('error')==0: _store_credential(payload)
                elif payload.get('error')==401:
                    time.sleep(5)
                    continue
                else:
                    shared['status']='Bridge rejected the approval request (code '+str(payload.get('error'))+').'
                    shared['owner']=None
                    return
            cipher=system.util.jsonDecode(system.file.readFileAsString(SECRET_FILE))
            with system.secrets.decrypt(cipher) as secret:
                stage='device list request'
                payload=_get('devices',secret.getSecretAsString())
            devices=(payload.get('data') or {}).get('device_list') or []
            shared['device_count']=len(devices)
            shared['meter_candidates']=[dict(serial_number=d.get('serial_number'),third_serial_number=d.get('third_serial_number'),model=d.get('model'),online=d.get('online'),
                capability_names=[c.get('capability') for c in d.get('capabilities',[]) if isinstance(c,dict)])
                for d in devices if isinstance(d,dict) and ('POW' in str(d.get('model','')).upper() or _has_id(d.get('tags',{})) or str(d.get('serial_number',''))==DEVICE_ID)]
            if not devices:
                shared.update(status='No devices synced in CUBE. Sync POWCT cottage in Add eWeLink-linked Devices.',online=False,power_w=None,power_kw=None,voltage_v=None,current_a=None)
                time.sleep(5)
                continue
            stage='meter identity and capability mapping'
            reading=decode_meter(select_meter(payload))
            reading['updated_ms']=system.date.toMillis(system.date.now())
            with _lock: shared.update(reading)
        except:
            with _lock:
                shared.update(online=False,power_w=None,power_kw=None,voltage_v=None,current_a=None)
                if stage=='meter identity and capability mapping':
                    shared['status']='POWCT identity or electrical mapping needs verification. Check Gateway diagnostics.'
                else: _failure(stage)
        finally:
            # Nonsecret telemetry evidence continues even when no phone is open.
            try:
                system.file.writeFile('C:/Users/Paul/OneDrive/Desktop/Ignition/home-scada/qa/meter-runtime.json',
                    system.util.jsonEncode(snapshot()))
            except:
                pass
        time.sleep(5)

def _start():
    shared=_shared()
    if not system.file.fileExists(SECRET_FILE) and time.time()>shared.get('authorize_until',0): return
    with _lock:
        if shared.get('owner') is _worker_id: return
        shared['owner']=_worker_id
        worker=threading.Thread(target=_run,name='HomeSCADA-CUBE-readonly')
        worker.setDaemon(True); worker.start()

def snapshot():
    _start()
    shared=_shared()
    with _lock:
        result={key:value for key,value in shared.items() if key not in ('owner','authorize_until')}
    now=system.date.toMillis(system.date.now())
    if result.get('online') and now-result.get('updated_ms',0)>15000:
        result.update(status='Meter reading stale',online=False,power_w=None,power_kw=None,voltage_v=None,current_a=None)
    return result
