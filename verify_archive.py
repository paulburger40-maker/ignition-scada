import hashlib,json,sqlite3
from pathlib import Path
root=Path(__file__).resolve().parent
db=sqlite3.connect(root/'ignition_knowledge.sqlite')
bad=[]; corrected=0
for id,name,digest in db.execute('SELECT id,local_file,sha256 FROM documents').fetchall():
 p=root/name
 if not p.exists(): bad.append(name); continue
 actual=hashlib.sha256(p.read_bytes()).hexdigest()
 if actual!=digest:
  # Earlier HTML saves used Windows newline translation while hashing LF text.
  if p.suffix=='.html' and hashlib.sha256(p.read_text(encoding='utf-8').encode()).hexdigest()==digest:
   db.execute('UPDATE documents SET sha256=? WHERE id=?',(actual,id)); corrected+=1
  else: bad.append(name)
db.commit()
manifest=json.loads((root/'knowledge/manifest.json').read_text())
for item in manifest['documents']:
 item['sha256']=db.execute('SELECT sha256 FROM documents WHERE url=?',(item['url'],)).fetchone()[0]
(root/'knowledge/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
report=dict(documents=db.execute('SELECT count(*) FROM documents').fetchone()[0],database_integrity=db.execute('PRAGMA integrity_check').fetchone()[0],indexed=db.execute('SELECT count(*) FROM search').fetchone()[0],archive_hash_failures=bad,newline_digest_corrections=corrected)
(root/'knowledge/verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
if bad: raise SystemExit(1)
