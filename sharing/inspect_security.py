from java.lang import Class
from com.inductiveautomation.ignition.common.gson import Gson
for name in ['com.inductiveautomation.ignition.common.xmlserialization.serialization.XMLSerializer','com.inductiveautomation.ignition.common.xmlserialization.deserialization.XMLDeserializer','com.inductiveautomation.ignition.common.ImmutableBytes','com.inductiveautomation.perspective.common.config.PerspectiveProjectProps','com.inductiveautomation.perspective.common.config.SessionPermissionsConfig','com.inductiveautomation.perspective.common.config.EventConfig']:
    try:
        c=Class.forName(name)
        print(name)
        for m in c.getDeclaredMethods():
            if any(x in m.getName().lower() for x in ['binary','gzip','deserialize','getbytes','getinstance','tobyte','newinstance','permission','security','json','resource','auth']): print(m.toString())
        if 'perspective.common.config' in name:
            print('Fields: '+str([str(f) for f in c.getDeclaredFields()]))
            try: print('Defaults: '+Gson().toJson(c.newInstance()))
            except: pass
    except: print('unavailable '+name)
