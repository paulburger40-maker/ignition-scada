"""Build the real equipment dashboard and unconfigured instrument slots."""
import datetime,hashlib,json,zipfile
from pathlib import Path
from resource_helpers import save,resource,binding,label,row,panel,metric

HERE=Path(__file__).resolve().parent
PROJECT=HERE/'project'
PAGES=[('Overview','/'),('Energy','/energy'),('EV Charging','/charging'),('Switches','/switches'),('Remote','/remote'),('Security','/security'),('Instruments','/integrations')]

def button(name,text,code,admin=False):
    lines=['try:']+['\t'+line for line in code.splitlines()]+[
        'except Exception as error:',
        '\tself.view.custom.actionFeedback = "Action failed. Please retry or report this message."',
        '\tsystem.util.getLogger("HomeSCADA.UI").warn("'+name+' failed: " + type(error).__name__)']
    result=dict(type='ia.input.button',meta=dict(name=name),position=dict(basis='42px',shrink=0),
        props=dict(text=text,style=dict(backgroundColor='#007f8b',color='#ffffff',border='none',borderRadius='10px',minWidth='150px',fontSize='14px',padding='8px 14px')),
        events=dict(component=dict(onActionPerformed=dict(type='script',scope='G',config=dict(script='\n'.join('\t'+line for line in lines))))))
    if admin: result['propConfig']={'props.enabled':binding('isAuthorized(false, "Authenticated/Roles/Administrator")')}
    return result

def add_button(kind,text='Add instrument'):
    return button('Add'+kind,text,'system.perspective.openPopup("instrument-slot", "Home/InstrumentSetup", params={"kind": "'+kind+'"}, modal=True, showCloseIcon=True, title="Add instrument slot", sessionId=self.session.props.id, pageId=self.page.props.pageId, viewportBound=True)',True)

def value(field,unit):
    expr='{view.custom.snapshot.cottage.'+field+'}'
    return 'if(isNull('+expr+'), "Unavailable", numberFormat('+expr+', "0.00") + " '+unit+'")'

def cottage():
    return panel('CottageMeter',[
        label('CottageTitle','POWCT COTTAGE',24),label('CottageModel','SONOFF POWCT · eWeLink · read only',14,'#566c7c'),
        label('CottageStatus',expression='{view.custom.snapshot.cottage.status}',color='#9b6612'),
        row('Electrical',[metric('CottagePower','Active power',value('power_w','W')),metric('CottageVoltage','Voltage',value('voltage_v','V')),metric('CottageCurrent','Current',value('current_a','A'))]),
        button('ConnectCottageMeter','Connect meter','self.view.custom.actionFeedback = "Requesting bridge connection..."\nself.view.custom.actionFeedback = home_scada.connect_meter(self.session.props.id)',True),
        label('MeterAccess','An administrator can authorize the bridge. Approve its API request in CUBE; connection retries automatically for two minutes.',13,'#566c7c'),
        label('MeterFeedback',expression='{view.custom.actionFeedback}',color='#007f8b'),
        label('MeterFreshness',size=13,expression='if({view.custom.snapshot.cottage.online}, "Recent device response · check units against eWeLink", "No verified fresh reading available")'),
        label('MeterBoundary','Cottage measurement only. Whole-house totals are not inferred from this meter.',13,'#566c7c')])

def slot(name,title,note,kind):
    return panel(name,[label(name+'Title',title,22),label(name+'State','Not connected',16,'#9b6612'),label(name+'Note',note,14,'#566c7c'),add_button(kind,'Set up instrument slot')])

def table(name,kind=None):
    config=binding('{view.custom.snapshot.instruments}')
    if kind: config['binding']['transforms']=[dict(type='script',code='\treturn [item for item in value if item["Type"] == "'+kind+'"]')]
    return dict(type='ia.display.table',meta=dict(name=name),position=dict(basis='270px',shrink=0),props=dict(data=[],selection=dict(enabled=False)),propConfig={'props.data':config})

def make_view(title,body):
    navigation=row('Navigation',[button('Nav'+str(i),name,'system.perspective.navigate(page="'+url+'", sessionId=self.session.props.id, pageId=self.page.props.pageId)') for i,(name,url) in enumerate(PAGES)])
    children=[label('Brand','MY HOME',13,'#007f8b'),row('Heading',[label('Title',title,32),label('Mode','REAL EQUIPMENT · READ ONLY',13,'#007f8b')]),
        row('Access',[label('AccessMode',size=13,expression='if(isAuthorized(false, "Authenticated/Roles/Administrator"), "Administrator · instrument setup", "Household access · view readings")'),button('Logout','Log out','system.perspective.logout(sessionId=self.session.props.id, pageId=self.page.props.pageId)')]),navigation,label('ActionFeedback',expression='{view.custom.actionFeedback}',color='#9b6612')]+body
    return dict(custom=dict(actionFeedback='',snapshot=dict(mode='Real equipment',instruments=[],cleanup_status='',cottage=dict(online=False,status='Bridge authorization needed',power_w=None,voltage_v=None,current_a=None,updated_ms=0))),params={},
        propConfig={'custom.snapshot':dict(binding=dict(type='expr',config=dict(expression='now(2000)'),transforms=[dict(type='script',code='\treturn home_scada.snapshot()')]))},props=dict(defaultSize=dict(width=1280,height=980)),
        root=dict(type='ia.container.flex',meta=dict(name='root'),props=dict(direction='column',style=dict(backgroundColor='#f4f7fa',padding='24px',gap='18px',overflowY='auto')),children=children))

def input_field(name,placeholder):
    return dict(type='ia.input.text-field',meta=dict(name=name),position=dict(basis='42px',shrink=0),props=dict(text='',placeholder=placeholder))

def setup_view():
    kind=dict(type='ia.input.dropdown',meta=dict(name='Kind'),position=dict(basis='42px',shrink=0),props=dict(options=[dict(value=k,label=k) for k in ('Meter','Charger','Switch','TV','Alexa','Security','Other')],value='Other'),propConfig={'props.value':binding('{view.params.kind}')})
    fields=[label('FormTitle','Add a real instrument slot',24),label('FormHelp','Save its identity now; connect and verify hardware separately. Do not enter passwords or keys here.',14),kind,input_field('SlotName','Instrument name'),input_field('Model','Brand and exact model'),input_field('Location','Room or location')]
    fields += [button('SaveSlot','Save slot','self.view.custom.feedback = home_scada.save_slot(self.getSibling("Kind").props.value, self.getSibling("SlotName").props.text, self.getSibling("Model").props.text, self.getSibling("Location").props.text, self.session.props.id)',True),label('FormFeedback',expression='{view.custom.feedback}',color='#007f8b')]
    return dict(custom=dict(feedback='',actionFeedback=''),params=dict(kind='Other'),props=dict(defaultSize=dict(width=520,height=420)),root=dict(type='ia.container.flex',meta=dict(name='root'),props=dict(direction='column',style=dict(padding='24px',gap='12px',backgroundColor='#ffffff')),children=fields))

def main():
    save(PROJECT/'project.json',dict(title='My Home',description='Real household equipment and unconfigured instrument slots',enabled=True,inheritable=False,parent=''))
    path=PROJECT/'ignition/startup'
    path.mkdir(parents=True,exist_ok=True)
    (path/'onStartup.py').write_text('def onStartup():\n\tcube_meter.snapshot()\n',encoding='utf-8')
    resource(path,['onStartup.py'],'G',dict(enabled=True))
    for name,source in [('home_scada','real_home_scada.py'),('cube_meter','cube_meter.py')]:
        path=PROJECT/'ignition/script-python'/name; path.mkdir(parents=True,exist_ok=True)
        (path/'code.py').write_text((HERE/'src'/source).read_text(encoding='utf-8'),encoding='utf-8'); resource(path,['code.py'],'A',dict(hintScope=2))
    bodies={
        'Overview':[cottage(),row('EquipmentSlots',[slot('EV','GEELY WALL CHARGER','Exact model and supported telemetry required.','Charger'),slot('Switches','SMART SWITCHES','Add each real switch with its room and model.','Switch'),slot('Security','TAPO SECURITY','Add the actual hub, cameras or sensors.','Security')]),label('Scope','Readings belong to connected equipment. Unconfigured instruments have no measurements or controls.',14)],
        'Energy':[cottage(),row('EnergyRecords',[panel('Consumption',[label('ConsumptionTitle','Energy consumption',22),label('Counters','Daily, monthly and cumulative kWh: not mapped',16,'#9b6612'),label('History','History: not commissioned',14),label('Tariff','Electricity cost: household tariff required',14)]),panel('EnergySlots',[label('EnergySlotsTitle','Additional meters',22),label('EnergySlotsNote','Add a meter slot for another supply, circuit, solar system or charger.',14),add_button('Meter','Add meter slot')])])],
        'EV Charging':[slot('Geely','Geely wall-mounted charger','Add its exact model. Available readings and controls will follow the supported interface.','Charger'),label('EVState','Charging state, current and session energy are unavailable until connected.',14)],
        'Switches':[slot('Geyser','Cottage geyser switch','Connection deferred. No on/off state is inferred.','Switch'),add_button('Switch','Add switch slot'),table('SwitchInventory','Switch')],
        'Remote':[row('RemoteSlots',[slot('TV','Smart TV','Add brand/model and supported local remote interface.','TV'),slot('Alexa','Alexa','Add the device and choose its supported integration.','Alexa')]),label('RemoteNote','Remote buttons become available after each real device is commissioned.',14)],
        'Security':[slot('Tapo','Tapo security system','Add actual cameras, hub and sensors. Their current state is unknown.','Security'),label('SecurityNote','Camera feeds, events and arming controls are unavailable until connected.',14)],
        'Instruments':[label('InventoryTitle','Real equipment and instrument slots',24),label('InventoryNote','A saved slot records an instrument to connect; it does not claim a working connection.',14),add_button('Other'),table('Inventory'),label('CleanupStatus',size=13,color='#566c7c',expression='{view.custom.snapshot.cleanup_status}')]
    }
    pages={}
    for title,url in PAGES:
        # Keep existing routes/view paths for saved household links.
        view_name='Integrations' if title=='Instruments' else title.replace(' ','')
        path=PROJECT/'com.inductiveautomation.perspective/views/Home'/view_name
        save(path/'view.json',make_view(title,bodies[title])); resource(path,['view.json'])
        pages[url]=dict(title='My Home · '+title,viewPath='Home/'+view_name,docks={})
    path=PROJECT/'com.inductiveautomation.perspective/views/Home/InstrumentSetup'; save(path/'view.json',setup_view()); resource(path,['view.json'])
    path=PROJECT/'com.inductiveautomation.perspective/page-config'; save(path/'config.json',dict(pages=pages)); resource(path,['config.json'])
    save(HERE/'device-registry.json',dict(project='home_scada',mode='Real equipment',meter=json.loads((HERE/'meter-commissioning.json').read_text()),physical_commands_enabled=False,planned_slots=['Geely charger','Smart switches','Alexa','Smart TV','Tapo security']))
    (HERE/'io-register.csv').write_text('Equipment,Measurement,Source,Units,ConnectionStatus,ReadWrite\nPOWCT cottage,ActivePower_W,CUBE electric-power,W,Awaiting authorization and unit verification,Read only\nPOWCT cottage,Voltage_V,CUBE voltage,V,Awaiting capability verification,Read only\nPOWCT cottage,Current_A,CUBE electric-current,A,Awaiting capability verification,Read only\n',encoding='utf-8')
    output=HERE/'home_scada-project.zip'
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        for p in PROJECT.rglob('*'):
            if p.is_file() and p.suffix!='.pyc' and '__pycache__' not in p.parts: z.write(p,p.relative_to(PROJECT).as_posix())
    save(HERE/'build-manifest.json',dict(project='home_scada',mode='Real equipment',generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),views=8,pages=7,simulated_instances=0,zip_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),imported=False,interactive_tested=False))
    print('Generated real equipment dashboard: 7 pages, 1 setup popup, no simulated readings or controls')

if __name__=='__main__': main()
