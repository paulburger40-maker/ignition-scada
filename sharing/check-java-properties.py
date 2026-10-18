from java.util import Properties
from java.io import FileInputStream
for name in ['sharing/phone-xml-staged.xml',r'C:/Program Files/Inductive Automation/Ignition/data/gateway.xml']:
 try:
  p=Properties(); f=FileInputStream(name)
  try: p.loadFromXML(f)
  finally: f.close()
  print(name+': PASS '+str(p.getProperty('gateway.publicAddress.autoDetect')))
 except Exception as e: print(name+': '+str(e))
