"""Real equipment dashboard. No generated readings or physical commands."""
import json, threading

_lock=threading.RLock()
_retired=False
_cleanup_status='Checking previous home tags'
ROOT='[default]HomeSCADA'
OWNER='home-scada-simulation-v1'
WORKSPACE='C:/Users/Paul/OneDrive/Desktop/Ignition/'
INVENTORY='C:/Users/Paul/IgnitionHome/private/instrument-slots.json'

def instruments(cottage=None):
    status=(cottage or {}).get('status','Authorization and telemetry verification pending')
    rows=[dict(Name='POWCT cottage',Type='Meter',Model='SONOFF POWCT',Location='Cottage',Connection=status)]
    if system.file.fileExists(INVENTORY):
        for item in json.loads(system.file.readFileAsString(INVENTORY)):
            rows.append(dict(Name=item['name'],Type=item['kind'],Model=item['model'],Location=item['location'],Connection='Not connected'))
    return rows

def save_slot(kind,name,model,location,session_id):
    if not session_id or not system.perspective.isAuthorized(False,['Authenticated/Roles/Administrator'],session_id):
        return 'Administrator access is required to add an instrument.'
    if kind not in ('Meter','Charger','Switch','TV','Alexa','Security','Other'):
        return 'Choose an instrument type.'
    values=[str(value or '').strip() for value in (name,model,location)]
    if not values[0] or any(len(value)>120 for value in values):
        return 'Enter a name and keep each field under 120 characters.'
    with _lock:
        items=json.loads(system.file.readFileAsString(INVENTORY)) if system.file.fileExists(INVENTORY) else []
        if any(item['name'].lower()==values[0].lower() for item in items) or values[0].lower()=='powct cottage':
            return 'An instrument with this name already exists.'
        items.append(dict(kind=kind,name=values[0],model=values[1],location=values[2]))
        system.file.writeFile(INVENTORY,json.dumps(items))
    return 'Slot saved. Close this window to see it in Instruments. Hardware is not connected yet.'

def initialize():
    global _retired,_cleanup_status
    with _lock:
        if _retired: return
        if not system.tag.exists(ROOT):
            _retired=True; _cleanup_status='Previous home tags retired'; return
        backup=WORKSPACE+'backups/before-real-only-20261010.gwbk'
        if not system.file.fileExists(backup):
            _cleanup_status='Retirement pending supported backup'; return
        owner=system.tag.readBlocking([ROOT+'/System/Owner'])[0]
        if not owner.quality.isGood() or str(owner.value)!=OWNER:
            _cleanup_status='Tag retirement stopped: ownership mismatch'; return
        archive=WORKSPACE+'backups/retired-home-tags-20261010.json'
        if not system.file.fileExists(archive):
            system.tag.exportTags(filePath=archive,tagPaths=[ROOT],recursive=True)
        results=system.tag.deleteTags([ROOT])
        if any(not q.isGood() for q in results):
            _cleanup_status='Previous tag retirement needs inspection'; return
        _retired=True; _cleanup_status='Previous home tags retired'
        system.util.getLogger('HomeSCADA').info('Retired owned home test instances; physical equipment unchanged')

def tick():
    return

def command(*args,**kwargs):
    raise RuntimeError('Physical controls are not commissioned')

def scene(*args,**kwargs):
    raise RuntimeError('Physical routines are not commissioned')

def connect_meter(session_id):
    try:
        cube_meter.authorize(session_id)
        return cube_meter.snapshot()['status']
    except:
        return 'Connection request failed. Administrator access and Gateway reader must be checked.'

def snapshot():
    try:
        initialize()
    except:
        pass
    try:
        cottage=cube_meter.snapshot()
    except:
        cottage=dict(online=False,status='Gateway meter reader unavailable',power_w=None,power_kw=None,
            voltage_v=None,current_a=None,firmware='Unreported',updated_ms=0,physical_commands_enabled=False)
    result=dict(mode='Real equipment',cottage=cottage,cleanup_status=_cleanup_status,instruments=instruments(cottage),
        physical_commands_enabled=False,tariff_configured=False,history_configured=False)
    # Nonsecret runtime evidence only; never request headers, credentials or user data.
    try:
        system.file.writeFile(WORKSPACE+'home-scada/qa/real-runtime.json',system.util.jsonEncode(result))
    except:
        pass
    return result
