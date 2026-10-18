"""Build the single cottage Overview, preserving the existing authentication resources."""
import copy,datetime,hashlib,json,shutil,uuid,zipfile
from pathlib import Path
from resource_helpers import save,resource,binding,label
HERE=Path(__file__).resolve().parent
OUT=HERE/'overview-project'
TEAL='#168a91'

def text(name,value='',size=14,color='#647887',height='26px',expression=None):
    c=label(name,value,size,color,height,expression)
    c['props']['style'].update(fontFamily='Segoe UI, sans-serif')
    return c

def flex(name,children,direction='column',basis='auto',grow=0,style=None,wrap='nowrap'):
    return dict(type='ia.container.flex',meta=dict(name=name),position=dict(basis=basis,grow=grow,shrink=0),
        props=dict(direction=direction,wrap=wrap,alignItems='stretch',style=style or {}),children=children)

def metric(name,title,field,unit,pattern):
    path='{view.custom.snapshot.cottage.'+field+'}'
    value='if(isNull('+path+'), "Unavailable", numberFormat('+path+', "'+pattern+'") + " '+unit+'")'
    c=flex(name,[text(name+'Title',title,12,height='24px'),text(name+'Value',size=27,color='#183a4b',height='44px',expression=value)],
        basis='100px',grow=1,style=dict(backgroundColor='#ffffff',borderRadius='12px',padding='14px',border='1px solid #e4ecef',minWidth='94px'))
    c['position']['shrink']=1
    return c

def chart(name,kind,source,height):
    example=json.loads((HERE/'qa/native-xy-example.json').read_text(encoding='utf-8'))['props']
    x=copy.deepcopy(example['xAxes'][0]);y=copy.deepcopy(example['yAxes'][0]);series=copy.deepcopy(example['series'][0])
    x.update(name='horizontal',render='date' if kind=='profile' else 'category')
    x['label']['enabled']=False;x['tooltip']['enabled']=True
    y.update(name='vertical',render='value');y['label'].update(enabled=True,text='kW' if kind=='profile' else 'kWh',color='#647887')
    y['value']['range'].update(min=0,max='',useStrict=False);y['value']['format']='#,##0.##'
    for axis in (x,y):
        axis['appearance']['labels'].update(color='#647887',rotation=0)
        axis['appearance']['font'].update(size=11,weight=400)
        axis['appearance']['grid'].update(color='#dce6eb',opacity=.55,minDistance=45)
    x['appearance']['grid']['opacity']=0
    if kind=='profile':
        x['date']['format']='HH:mm';x['date']['inputFormat']='x'
        x['date']['baseInterval'].update(enabled=True,timeUnit='minute',count=1,skipEmptyPeriods=False)
        x['date']['range'].update(min=0,max=1,useStrict=True)
    series.update(name='recorded',label=dict(text='Power' if kind=='profile' else 'Recorded energy'),render='line' if kind=='profile' else 'column',
        xAxis='horizontal',yAxis='vertical',hiddenInLegend=True)
    series['data']=dict(source=source,x='time' if kind=='profile' else 'period',y='power_kw' if kind=='profile' else 'energy_kwh')
    series['tooltip'].update(enabled=True,text='{valueY.formatNumber("#,##0.000")} kW' if kind=='profile' else '{categoryX}: {valueY.formatNumber("#,##0.000")} kWh\n{coverage} · {completeness}\n{basis}')
    series['line']['appearance'].update(connect=False)
    series['line']['appearance']['stroke'].update(color=TEAL,width=2)
    series['line']['appearance']['fill'].update(color=TEAL,opacity=.08)
    for bullet in series['line']['appearance']['bullets']:bullet['enabled']=False
    series['column']['appearance']['fill'].update(color=TEAL,opacity=1)
    series['column']['appearance']['stroke'].update(color=TEAL,opacity=0)
    series['column']['appearance']['deriveFieldsFromData']['fill']['color']='bar_color'
    all_series=[series]
    props=dict(dataSources={source:[]},xAxes=[x],yAxes=[y],series=all_series,legend=dict(enabled=False),
        cursor=dict(enabled=True,series='recorded'),enableTransitions=False,scrollBars=dict(horizontal=dict(enabled=False),vertical=dict(enabled=False)),
        selection=dict(enabled=False),background=dict(render='color',color='#ffffff',opacity=1),style=dict(fontFamily='Segoe UI, sans-serif'))
    bindings={'props.dataSources.'+source:binding('{view.custom.snapshot.history.'+source+'}')}
    if kind=='profile':
        instant=copy.deepcopy(series);instant.update(name='instant',label=dict(text='Live power'),data=dict(source='live',x='time',y='power_kw'))
        instant['line']['appearance']['stroke']['opacity']=0
        instant['line']['appearance']['fill']['opacity']=0
        bullet=instant['line']['appearance']['bullets'][0]
        bullet.update(enabled=True,width=9,height=9)
        bullet['fill'].update(color=TEAL,opacity=1);bullet['stroke'].update(color='#ffffff',width=2)
        props['series'].append(instant);props['dataSources']['live']=[]
        bindings['props.dataSources.live']=binding('{view.custom.snapshot.history.live}')
        bindings['props.xAxes[0].date.range.min']=binding('{view.custom.snapshot.range_start}')
        bindings['props.xAxes[0].date.range.max']=binding('{view.custom.snapshot.range_end}')
    return dict(type='ia.chart.xy',meta=dict(name=name),position=dict(basis=str(height)+'px',grow=0,shrink=0),props=props,propConfig=bindings)

def chart_card(name,title,subtitle,kind,source,height):
    heading=[text(name+'Title',title,18,'#183a4b','30px')]
    if kind=='profile':
        heading.append(text(name+'Now',size=14,color=TEAL,height='26px',expression='if({view.custom.snapshot.cottage.online}, "LIVE  " + numberFormat({view.custom.snapshot.cottage.power_kw}, "0.000") + " kW", "Live power unavailable")'))
    else:heading.append(text(name+'Subtitle',subtitle,12,height='24px'))
    c=flex(name,heading+[chart(name+'Figure',kind,source,height)],style=dict(backgroundColor='#ffffff',border='1px solid #e4ecef',borderRadius='14px',padding='18px',gap='3px'))
    return c

def build_view():
    header=flex('Header',[text('Cottage','Cottage',28,'#183a4b','42px'),text('Connection',size=12,color=TEAL,height='24px',expression='{view.custom.snapshot.connection}')],style=dict(gap='0px'))
    tab=text('OverviewTab','Overview',14,TEAL,'36px');tab['props']['style'].update(borderBottom='2px solid '+TEAL,maxWidth='94px',fontWeight=600)
    metrics=flex('LiveReadings',[metric('Power','POWER NOW','power_kw','kW','0.000'),metric('Voltage','VOLTAGE','voltage_v','V','0.0'),metric('Current','CURRENT','current_a','A','0.00')],
        direction='row',style=dict(gap='10px',minHeight='100px'))
    profile=chart_card('Profile','Power · last 24 hours','','profile','profile',300)
    daily=chart_card('Daily','Daily energy','Last 7 days · kWh','bar','daily',240)
    monthly=chart_card('Monthly','Monthly energy','Last 12 months · kWh','bar','monthly',240)
    for card in (daily,monthly):
        card['position'].update(basis='420px',grow=1,shrink=1);card['props']['style']['minWidth']='280px'
    history=flex('EnergyTotals',[daily,monthly],direction='row',wrap='wrap',style=dict(gap='16px'))
    note=text('HistoryNote',size=12,height='auto',expression='{view.custom.snapshot.history_note}')
    note['props']['style'].update(whiteSpace='normal',minHeight='52px')
    root=flex('root',[header,tab,metrics,profile,history,note],style=dict(backgroundColor='#f4f7f9',padding='18px',gap='16px',overflowY='auto',overflowX='hidden'))
    root.pop('position')
    return dict(custom=dict(snapshot=dict(connection='Connecting',cottage=dict(online=False,power_kw=None,voltage_v=None,current_a=None),
        history=dict(profile=[],live=[],daily=[],monthly=[]),range_start=0,range_end=1,history_note='Loading recorded history')),
        params={},props=dict(defaultSize=dict(width=1180,height=1050)),root=root,
        propConfig={'custom.snapshot':dict(binding=dict(type='expr',config=dict(expression='now(2000)'),transforms=[dict(type='script',code='\treturn home_scada.snapshot()')]))})

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'project.json',dict(title='My Home',description='Cottage electricity overview',enabled=True,inheritable=False,parent=''))
    for relative in ['ignition/global-props','com.inductiveautomation.perspective/session-permissions','com.inductiveautomation.perspective/props']:
        source=HERE/'project'/relative
        if source.exists():shutil.copytree(source,OUT/relative,dirs_exist_ok=True)
    for name,source in [('home_scada','overview_gateway.py'),('cube_meter','cube_meter.py'),('cottage_history','cottage_history.py'),('cottage_energy','cottage_energy.py')]:
        p=OUT/'ignition/script-python'/name;p.mkdir(parents=True,exist_ok=True)
        (p/'code.py').write_text((HERE/'src'/source).read_text(encoding='utf-8'),encoding='utf-8');resource(p,['code.py'],'A',dict(hintScope=2))
    p=OUT/'ignition/startup';p.mkdir(parents=True,exist_ok=True)
    (p/'onStartup.py').write_text('def onStartup():\n\tcottage_history.start()\n\tcube_meter.snapshot()\n\thome_scada.snapshot()\n',encoding='utf-8');resource(p,['onStartup.py'],'G',dict(enabled=True))
    p=OUT/'com.inductiveautomation.perspective/views/Home/Overview';save(p/'view.json',build_view());resource(p,['view.json'])
    # /energy is a compatibility alias for existing phone/browser bookmarks; no second tab.
    p=OUT/'com.inductiveautomation.perspective/page-config';save(p/'config.json',dict(pages={u:dict(title='Cottage · Overview',viewPath='Home/Overview',docks={}) for u in ('/','/energy')}));resource(p,['config.json'])
    target=HERE/'home_scada-overview.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for p in OUT.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(OUT).as_posix())
    save(HERE/'overview-build-manifest.json',dict(generatedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),views=1,visible_tabs=1,charts=3,real_only=True,
        archive_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),native_imported=False,interactive_tested=False))
    print('Built one cottage Overview, three real-data charts, existing authentication preserved')

if __name__=='__main__':main()
