"""Bounded development sync of this one generated project; never deletes files."""
import datetime,hashlib,json,re,shutil,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'project'
TARGET=Path('C:/Program Files/Inductive Automation/Ignition/data/projects/home_scada')
STOP=HERE/'stop-sync.flag'
assert TARGET.resolve()==Path('C:/Program Files/Inductive Automation/Ignition/data/projects/home_scada').resolve()
assert (TARGET/'project.json').exists(), 'Target project must already exist'
deadline=time.monotonic()+600
copied=0
while time.monotonic()<deadline and not STOP.exists():
    files=[f for f in SOURCE.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc']
    for resource in SOURCE.rglob('resource.json'):
        d=json.loads(resource.read_text(encoding='utf-8'))
        stamp=d['attributes']['lastModification']['timestamp']
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',stamp): raise ValueError('Invalid native UTC metadata timestamp')
        datetime.datetime.strptime(stamp,'%Y-%m-%dT%H:%M:%SZ')
    for f in files:
        relative=f.relative_to(SOURCE)
        dest=TARGET/relative
        if dest.exists() and hashlib.sha256(dest.read_bytes()).digest()==hashlib.sha256(f.read_bytes()).digest(): continue
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(f,dest)
        copied+=1
        print('Updated',relative,flush=True)
    time.sleep(2)
print('Development sync ended. Files copied:',copied,flush=True)
