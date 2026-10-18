from java.lang import Class
ProjectScriptModule=Class.forName('com.inductiveautomation.ignition.common.script.ProjectScriptModule')
print('Constructors: '+str(ProjectScriptModule.getConstructors()))
for m in ProjectScriptModule.getMethods():
    if any(s in m.getName().lower() for s in ['startup','shutdown','script','resource','instance']): print(m.toString())
for f in ProjectScriptModule.getFields(): print(str(f))
