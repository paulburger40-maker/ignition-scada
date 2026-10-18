from java.lang import Class
from com.inductiveautomation.ignition.common.project import GlobalProps
print('GlobalProps methods:')
for m in GlobalProps.getDeclaredMethods():
    print(m.toString())
for name in ['com.inductiveautomation.ignition.common.xmlserialization.serialization.XMLSerializer','com.inductiveautomation.ignition.common.xmlserialization.deserialization.XMLDeserializer','com.inductiveautomation.ignition.common.auth.permissions.PermissionsConfig','com.inductiveautomation.ignition.common.resourcecollection.Resource']:
    try:
        c=Class.forName(name)
        print(name)
        for m in c.getDeclaredMethods():
            print(m.toString())
    except: print('unavailable ' + name)
