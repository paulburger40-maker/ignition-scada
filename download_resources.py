import datetime, hashlib, json
from pathlib import Path
from urllib.request import Request, urlopen

root=Path(__file__).resolve().parent/'knowledge'/'scada-design'
root.mkdir(parents=True,exist_ok=True)
resources={
 'Design-Like-a-Pro-Foundation.pdf':'https://pages.inductiveautomation.com/rs/inductiveautomation/images/Design_Like_a_Pro_Part_1_Laying_the_Foundation.pdf',
 'Optimizing-Your-HMI.pdf':'https://assets.inductiveautomation.com/s3fs-production/test_folder/DLAP-Optimizing-Your-HMI.pdf',
 'Ignition-Deployment-Best-Practices.pdf':'https://assets.inductiveautomation.com/s3fs-production/test_folder/Ignition%208%20Deployment%20Best%20Practices_0.pdf',
 'Design-Like-a-Pro-Part-2.html':'https://inductiveautomation.com/resources/article/design-like-a-pro-part-2',
 'Inductive-University-8.3-Databases.html':'https://inductiveuniversity.com/courses/ignition/databases-in-ignition/8.3'
}
records=[]
for name,url in resources.items():
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as r: data=r.read()
  if name.endswith('.pdf') and not data.startswith(b'%PDF'): raise ValueError('Response is not a PDF')
  (root/name).write_bytes(data)
  records.append(dict(file=name,url=url,retrieved=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),status='downloaded'))
  print('Downloaded',name,flush=True)
 except Exception as e: records.append(dict(file=name,url=url,status='failed',error=str(e))); print('Failed',name,str(e),flush=True)
(root/'manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
