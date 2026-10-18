from java.nio.file import Files, Paths
from com.inductiveautomation.ignition.common.project import GlobalProps
from com.inductiveautomation.ignition.common.auth.permissions import PermissionsConfig
from com.inductiveautomation.ignition.common.gson import JsonParser
g=GlobalProps.newInstance()
g.setIdp('default')
g.setAuthProfileName('default')
g.setAutoIdpAuth(True)
g.setForceIdpAuth(False)
g.setDefaultSQLTagsProviderName('default')
r=g.toResource('home_scada')
p=Paths.get('home-scada/project/ignition/global-props/data.bin')
Files.createDirectories(p.getParent())
Files.write(p,r.getData('data.bin').get().getBytes())
raw='{"type":"AnyOf","securityLevels":[{"name":"Authenticated","children":[{"name":"Roles","children":[{"name":"HomeViewer","children":[]},{"name":"HomeOperator","children":[]},{"name":"Administrator","children":[]}]}]}]}'
try:
    pc=PermissionsConfig.fromJsonTree(JsonParser().parse(raw))
    print('Validated permissions: '+str(pc.toJsonTree()))
except:
    raw='{"type":"AnyOf","securityLevels":["Authenticated/Roles/HomeViewer","Authenticated/Roles/HomeOperator","Authenticated/Roles/Administrator"]}'
    pc=PermissionsConfig.fromJsonTree(JsonParser().parse(raw))
    print('Validated permissions: '+str(pc.toJsonTree()))
p=Paths.get('sharing/session-permissions-validated.json')
Files.write(p,str(pc.toJsonTree()).encode('utf-8'))
