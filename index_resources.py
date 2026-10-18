import datetime, hashlib, json, re, sqlite3
from pathlib import Path
from pypdf import PdfReader
from build_knowledge import Text
root=Path(__file__).resolve().parent
db=sqlite3.connect(root/'ignition_knowledge.sqlite',timeout=30)
for record in json.loads((root/'knowledge/scada-design/manifest.json').read_text()):
 if record['status']!='downloaded': continue
 path=root/'knowledge/scada-design'/record['file']
 if path.suffix=='.pdf':
  reader=PdfReader(path); body='\n\n'.join(f'Page {i+1}\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages))
  version='General SCADA guidance; publication may predate Ignition 8.3'
 else:
  parser=Text(); parser.feed(path.read_text(encoding='utf-8')); body=''.join(parser.parts)
  version='8.3 training' if 'University' in path.name else 'General SCADA guidance'
 title=path.stem.replace('-',' ')
 db.execute('INSERT OR REPLACE INTO documents(url,title,version,retrieved,sha256,local_file,body) VALUES(?,?,?,?,?,?,?)',(record['url'],title,version,record['retrieved'],record['sha256'],str(path.relative_to(root)),body)); db.commit()
 print('Indexed',path.name,'characters',len(body))
db.execute('DELETE FROM search'); db.execute('INSERT INTO search(rowid,title,body,url) SELECT id,title,body,url FROM documents'); db.commit()
print('Total searchable documents:',db.execute('SELECT count(*) FROM documents').fetchone()[0])
