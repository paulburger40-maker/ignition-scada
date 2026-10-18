"""Replace active generation entry points; the prior version is already archived."""
from pathlib import Path
import ast
HERE=Path(__file__).parent
path=HERE/'build_home_scada.py'
source=path.read_text()
names={'save','resource','binding','label','row','panel','metric'}
chunks=[ast.get_source_segment(source,node) for node in ast.parse(source).body if isinstance(node,ast.FunctionDef) and node.name in names]
assert len(chunks)==7, 'Run once against the previous generation entry point'
(HERE/'resource_helpers.py').write_text("import json, datetime\nSTAMP=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')\n\n"+'\n\n'.join(chunks)+'\n')
path.write_text('"""Default build entry point: real equipment only."""\nfrom build_real_home_scada import main\nif __name__=="__main__": main()\n')
path=HERE/'build_real_home_scada.py'
path.write_text(path.read_text().replace('from build_home_scada import save,resource,binding,label,row,panel,metric','from resource_helpers import save,resource,binding,label,row,panel,metric'))
(HERE/'src/home_scada.py').write_text((HERE/'src/real_home_scada.py').read_text())
(HERE/'gateway-timer.py').write_text('# No generated data. Only the read-only device poller is active.\npass\n')
(HERE/'tags/instances.json').write_text('{"tags": []}')
(HERE/'tags/udt-definitions.json').write_text('{"tags": []}')
# The simulator tests are retained solely in the earlier source archive.
(HERE/'test_model.py').write_text('"""Compatibility entry point for current real-equipment checks."""\nfrom test_real_model import *\nif __name__=="__main__": unittest.main(verbosity=2)\n')
print('Active build entry points now generate only real equipment resources')
