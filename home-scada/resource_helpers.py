import json, datetime
STAMP=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2),encoding='utf-8')

def resource(path,files,scope='G',attributes=None):
    save(path/'resource.json',dict(scope=scope,version=1,restricted=False,overridable=True,files=files,
         attributes=dict(lastModification=dict(actor='home-scada-build',timestamp=STAMP),**(attributes or {}))))

def binding(expression): return dict(binding=dict(type='expr',config=dict(expression=expression)))

def label(name,text='',size=16,color='#152638',height='auto',expression=None):
    c=dict(type='ia.display.label',meta=dict(name=name),position=dict(basis=height,shrink=0),props=dict(text=text,style=dict(fontSize=str(size)+'px',color=color)))
    if expression: c['propConfig']={'props.text':binding(expression)}
    return c

def row(name,children):
    for child in children:
        if child.get('type')=='ia.input.button': child['position']['basis']='144px'
    return dict(type='ia.container.flex',meta=dict(name=name),position=dict(shrink=0),props=dict(direction='row',wrap='wrap',alignItems='stretch',style=dict(gap='12px')),children=children)

def panel(name,children):
    return dict(type='ia.container.flex',meta=dict(name=name),position=dict(basis='260px',grow=1,shrink=1),props=dict(direction='column',style=dict(backgroundColor='#ffffff',borderRadius='14px',padding='20px',gap='12px',border='1px solid #dce6ee')),children=children)

def metric(name,title,expression):
    return panel(name,[label(name+'Title',title,13,'#566c7c'),label(name+'Value',size=32,expression=expression)])
