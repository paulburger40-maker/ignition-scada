"""Use Ignition's Java runtime to preserve the required Java-properties XML format."""
import sys
from java.util import Properties
from java.io import FileInputStream, FileOutputStream

path=sys.argv[1]
changes={
    'gateway.publicAddress.autoDetect':'false',
    'gateway.publicAddress.address':'home-scada.tail78dd75.ts.net',
    'gateway.publicAddress.httpPort':'80',
    'gateway.publicAddress.httpsPort':'443',
    'gateway.useProxyForwardedHeader':'true',
}
p=Properties()
stream=FileInputStream(path)
try: p.loadFromXML(stream)
finally: stream.close()
for key,value in changes.items():
    if not p.containsKey(key): raise ValueError('Expected Gateway setting missing: '+key)
    p.setProperty(key,value)
stream=FileOutputStream(path)
try: p.storeToXML(stream,'Context Settings','UTF-8')
finally: stream.close()
verified=Properties()
stream=FileInputStream(path)
try: verified.loadFromXML(stream)
finally: stream.close()
for key,value in changes.items():
    if verified.getProperty(key)!=value: raise ValueError('Java settings verification failed')
print('Java properties XML loaded, saved and reloaded successfully')
