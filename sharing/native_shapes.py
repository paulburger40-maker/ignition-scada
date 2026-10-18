from java.lang import Class
from com.inductiveautomation.ignition.common.project import GlobalProps
from com.inductiveautomation.ignition.common.gson import Gson
from com.inductiveautomation.perspective.common.config import SessionPermissionsConfig, PerspectiveProjectProps
from com.inductiveautomation.ignition.common.auth.permissions import PermissionsConfig
for c in [SessionPermissionsConfig,PerspectiveProjectProps,PermissionsConfig]:
    print(c.getName())
    print('Constructors: '+str(c.getConstructors()))
    print('Parent: '+str(c.getSuperclass()))
    for m in c.getMethods():
        if any(x in m.getName().lower() for x in ['json','resource','config','security','permission','build']): print(m.toString())
    for f in c.getFields():
        if f.getName()=='RESOURCE_TYPE':
            t=f.get(None)
            print('RESOURCE_TYPE='+str(t))
            for m in t.getClass().getMethods():
                if m.getName() in ['getTypeId','getModuleId','getFolderName']: print(m.getName()+'='+str(m.invoke(t,[])))
g=GlobalProps.newInstance(); g.setIdp('default'); g.setAutoIdpAuth(True)
r=g.toResource('home_scada')
print('Global resource keys: '+str(r.getDataKeys()))
for k in r.getDataKeys():
    b=r.getData(k).get(); print('bytes methods: '+str([m.getName() for m in b.getClass().getMethods() if 'byte' in m.getName().lower()]))
