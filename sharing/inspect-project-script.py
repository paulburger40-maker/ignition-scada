from com.inductiveautomation.ignition.common.script import ScriptConfig
from com.inductiveautomation.ignition.common.resourcecollection import Resource
from com.inductiveautomation.ignition.common.gson import Gson
b=Resource.newBuilder(); b.setResourcePath(ScriptConfig.StartupScript.RESOURCE_TYPE.childPath("_unary")); b.setUnary(True); b.setResourceCollectionName('home_scada')
ScriptConfig.StartupScript.serialize('home_scada.snapshot()',True,ScriptConfig.StartupScript.DESCRIPTOR).accept(b)
r=b.build()
print('attributes='+Gson().toJson(r.getAttributes()))
print('data='+str(r.getDataKeys()))
for k in r.getDataKeys():
 print(k); print(r.getData(k).get().getBytesAsString())
print('unary',r.isUnary(),'path',str(r.getResourcePath()))



