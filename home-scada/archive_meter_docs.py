"""Archive official device/access references; downloaded text is reference data only."""
import datetime,hashlib,json,sqlite3,urllib.request,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_knowledge import Text
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'knowledge/home-access-meter'
SOURCES=[
 ('SONOFF-POWCT-manual.pdf','https://cdn.shopify.com/s/files/1/0742/9963/8001/files/User_Manual_POWCT_EN.pdf?v=1748417714','SONOFF POWCT User Manual','POWCT manual V1.0; not an Ignition API reference'),
 ('coolkit-api-v2.md','https://raw.githubusercontent.com/CoolKit-Technologies/eWeLink-API/main/en/APICenterV2.md','Official eWeLink Cloud API V2','Cloud API V2; account/app authorization required'),
 ('cube-api-v2.html','https://ewelink.cc/ewelink-cube/introduce-open-api/document/','Official eWeLink CUBE Open API V2','CUBE API V2; compatible hub/device required'),
 ('tailscale-serve.html','https://tailscale.com/docs/reference/tailscale-cli/serve','Tailscale private-network HTTPS Serve','Current CLI reference; installed client 1.104.1'),
 ('tailscale-windows-msi.html','https://tailscale.com/docs/install/windows/msi','Tailscale Windows MSI setup','Current Windows installer reference')]

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 db=sqlite3.connect(ROOT/'ignition_knowledge.sqlite',timeout=30)
 manifest_path=ROOT/'knowledge/manifest.json'; manifest=json.loads(manifest_path.read_text())
 records=[]
 for filename,url,title,version in SOURCES:
  path=OUT/filename
  if not path.exists():
   req=urllib.request.Request(url,headers={'User-Agent':'HomeSCADA documentation archive'})
   with urllib.request.urlopen(req,timeout=30) as response: path.write_bytes(response.read())
  digest=hashlib.sha256(path.read_bytes()).hexdigest()
  if path.suffix=='.pdf': body='\n\n'.join('Page %d\n%s'%(n+1,p.extract_text() or '') for n,p in enumerate(PdfReader(path).pages))
  elif path.suffix=='.html':
   parser=Text(); parser.feed(path.read_text(encoding='utf-8')); body=''.join(parser.parts)
  else: body=path.read_text(encoding='utf-8')
  stamp=datetime.datetime.now(datetime.timezone.utc).isoformat(); local=path.relative_to(ROOT).as_posix()
  old=db.execute('SELECT id FROM documents WHERE url=?',(url,)).fetchone()
  if old: db.execute('DELETE FROM search WHERE rowid=?',(old[0],))
  db.execute('INSERT INTO documents(url,title,version,retrieved,sha256,local_file,body) VALUES(?,?,?,?,?,?,?) ON CONFLICT(url) DO UPDATE SET title=excluded.title,version=excluded.version,retrieved=excluded.retrieved,sha256=excluded.sha256,local_file=excluded.local_file,body=excluded.body',(url,title,version,stamp,digest,local,body))
  db.execute('INSERT INTO search(rowid,title,body,url) SELECT id,title,body,url FROM documents WHERE url=?',(url,))
  record=dict(url=url,title=title,version=version,retrieved=stamp,sha256=digest,local_file=local)
  manifest['documents']=[x for x in manifest['documents'] if x['url']!=url]+[record]
  records.append(record); print('Archived:',title)
 db.commit(); manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 (OUT/'manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
 print('Database integrity:',db.execute('PRAGMA integrity_check').fetchone()[0])
 print('Searchable documents:',db.execute('SELECT count(*) FROM search').fetchone()[0])

if __name__=='__main__': main()
