"""Archive public official Ignition manual pages and index them locally."""
import argparse, datetime, hashlib, html, json, re, sqlite3, time, sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parent
BASE = 'https://docs.inductiveautomation.com'
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0; self.links=[]
    def handle_starttag(self, tag, attrs):
        if tag=='a': self.links.extend(v for k,v in attrs if k=='href' and v)
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','div','h1','h2','h3','li','pre','tr','br'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)
def fetch(url):
    cached=ROOT/'knowledge'/'manual-8.3'/(hashlib.sha256(url.encode()).hexdigest()[:16]+'.html')
    if cached.exists(): return cached.read_text(encoding='utf-8')
    with urlopen(Request(url,headers={'User-Agent':'IgnitionLocalKnowledge/1.0 (personal reference archive)'}),timeout=40) as r:
        return r.read().decode('utf-8','replace')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--limit',type=int,default=180); ap.add_argument('--search'); args=ap.parse_args()
    db=sqlite3.connect(ROOT/'ignition_knowledge.sqlite')
    db.execute('CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY,url TEXT UNIQUE,title TEXT,version TEXT,retrieved TEXT,sha256 TEXT,local_file TEXT,body TEXT)')
    db.execute('CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(title,body,url UNINDEXED)')
    if args.search:
        for row in db.execute("SELECT title,url,snippet(search,1,'[',']','...',32) FROM search WHERE search MATCH ? ORDER BY rank LIMIT 8",(args.search,)): print('\n'.join(row),'\n')
        return
    archive=ROOT/'knowledge'/'manual-8.3'; archive.mkdir(parents=True,exist_ok=True)
    seeds=['/docs/8.3/intro','/docs/8.3/getting-started','/docs/8.3/platform','/docs/8.3/ignition-modules/perspective','/docs/8.3/platform/tags','/docs/8.3/platform/scripting','/docs/8.3/platform/alarming','/docs/8.3/platform/database-connections','/docs/8.3/getting-started/startup-guide/downloading-and-installing-ignition']
    queue=[BASE+x for x in seeds]; seen=set(); failures=[]; count=0
    pool=ThreadPoolExecutor(max_workers=6); pending={}
    while queue and count<args.limit:
        url=queue.pop(0)
        if url in seen: continue
        seen.add(url)
        try:
            source=pending.pop(url).result() if url in pending else fetch(url)
            links=Text(); links.feed(source)
            for link in links.links:
                candidate=urljoin(url,html.unescape(link)).split('#')[0].split('?')[0].rstrip('/')
                if candidate.startswith(BASE+'/docs/8.3/') and not candidate.endswith('.md') and candidate not in seen and candidate not in queue: queue.append(candidate)
            article=re.search(r'<article\b[^>]*>(.*?)</article>',source,re.S)
            if not article: raise ValueError('No manual article found')
            parser=Text(); parser.feed(article.group(1)); body=re.sub(r'\n\s*\n+', '\n\n',''.join(parser.parts)).strip()
            title=re.search(r'<title[^>]*>(.*?)</title>',source,re.S); title=html.unescape(title.group(1)) if title else url
            name=hashlib.sha256(url.encode()).hexdigest()[:16]+'.html'; (archive/name).write_text(source,encoding='utf-8')
            db.execute('INSERT OR REPLACE INTO documents(url,title,version,retrieved,sha256,local_file,body) VALUES(?,?,?,?,?,?,?)',(url,title,'8.3',datetime.datetime.now(datetime.timezone.utc).isoformat(),hashlib.sha256((archive/name).read_bytes()).hexdigest(),str((archive/name).relative_to(ROOT)),body)); db.commit()
            count+=1
            if count%10==0: print(f'Archived {count} pages; queued {len(queue)}',flush=True)
            for upcoming in queue[:12]:
                if upcoming not in pending and upcoming not in seen: pending[upcoming]=pool.submit(fetch,upcoming)
        except Exception as e: failures.append({'url':url,'error':str(e)}); print('Unavailable:',url,str(e),flush=True)
    pool.shutdown(wait=True)
    db.execute('DELETE FROM search'); db.execute('INSERT INTO search(rowid,title,body,url) SELECT id,title,body,url FROM documents'); db.commit()
    rows=[dict(zip(['url','title','version','retrieved','sha256','local_file'],r)) for r in db.execute('SELECT url,title,version,retrieved,sha256,local_file FROM documents')]
    (ROOT/'knowledge'/'manifest.json').write_text(json.dumps({'documents':rows,'failures':failures,'remaining_urls':queue},indent=2),encoding='utf-8')
    print(f'Indexed {len(rows)} documents; {len(failures)} failures',flush=True)
if __name__=='__main__': main()
