"""Verify removal of generated data, stale-value handling and ownership-safe retirement."""
import importlib.util,json,types,unittest,datetime
from pathlib import Path
HERE=Path(__file__).parent

class Tests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('real_home_test',HERE/'src/real_home_scada.py')
        self.model=importlib.util.module_from_spec(spec); spec.loader.exec_module(self.model)
        self.deleted=[]; self.exports=[]; self.files={}; self.present=True; self.owner=self.model.OWNER
        good=types.SimpleNamespace(isGood=lambda:True)
        self.model.system=types.SimpleNamespace(
            tag=types.SimpleNamespace(exists=lambda p:self.present,readBlocking=lambda p:[types.SimpleNamespace(quality=good,value=self.owner)],
                exportTags=lambda **kw:self.exports.append(kw),deleteTags=lambda p:self.deleted.extend(p) or [good]),
            file=types.SimpleNamespace(fileExists=lambda p:p in self.files,readFileAsString=lambda p:self.files[p],writeFile=lambda p,v:self.files.update({p:v})),
            util=types.SimpleNamespace(jsonEncode=json.dumps,getLogger=lambda n:types.SimpleNamespace(info=lambda s:None)),
            perspective=types.SimpleNamespace(isAuthorized=lambda all,levels,sid:sid=='admin'))
        self.model.cube_meter=types.SimpleNamespace(snapshot=lambda:dict(online=False,power_w=None,status='Not connected'))
    def test_no_generated_values_or_commands(self):
        self.present=False
        value=self.model.snapshot()
        self.assertIsNone(value['cottage']['power_w']); self.assertFalse(value['physical_commands_enabled'])
        self.assertNotIn('history',value); self.assertNotIn('ev',value)
        for method in (self.model.command,self.model.scene):
            with self.assertRaises(RuntimeError): method('anything')
        self.model.tick(); self.assertEqual(self.deleted,[])
    def test_connected_meter_does_not_request_another_api_grant(self):
        grants=[]
        self.model.cube_meter=types.SimpleNamespace(snapshot=lambda:dict(online=True),authorize=grants.append)
        self.assertIn('connected',self.model.connect_meter('admin'))
        self.assertEqual(grants,[])
    def test_retirement_requires_backup_and_ownership(self):
        self.model.initialize(); self.assertEqual(self.deleted,[])
        self.files[self.model.WORKSPACE+'backups/before-real-only-20261010.gwbk']='backup'
        self.owner='other-owner'; self.model.initialize(); self.assertEqual(self.deleted,[])
        self.owner=self.model.OWNER; self.model.initialize()
        self.assertEqual(self.deleted,['[default]HomeSCADA']); self.assertEqual(len(self.exports),1)
        self.model.initialize(); self.assertEqual(len(self.deleted),1)
    def test_inventory_is_configuration_only_and_admin_only(self):
        self.assertIn('Administrator',self.model.save_slot('Switch','Kitchen','Unknown','Kitchen','viewer'))
        self.assertNotIn(self.model.INVENTORY,self.files)
        self.assertIn('Slot saved',self.model.save_slot('Switch','Kitchen','Unknown','Kitchen','admin'))
        rows=self.model.instruments(); self.assertEqual(rows[-1]['Connection'],'Not connected')
        self.assertNotIn('On',rows[-1]); self.assertNotIn('Power',rows[-1])
        self.assertIn('already exists',self.model.save_slot('Switch','Kitchen','','','admin'))
    def test_active_resources_contain_no_demo_ui_or_writes(self):
        project=HERE/'project'
        for path in project.rglob('view.json'):
            text=path.read_text(); self.assertNotRegex(text.lower(),r'\bdemo\b|\bsimulation\b|simulat[eio]|home_scada\.command|home_scada\.scene')
            def walk(value):
                if isinstance(value,dict):
                    if value.get('type')=='script':
                        code=value.get('code') or value.get('config',{}).get('script')
                        if code: compile('def test(self, value=None, quality=None, timestamp=None, event=None):\n'+code,'native-event','exec')
                    for item in value.values(): walk(item)
                elif isinstance(value,list):
                    for item in value: walk(item)
            walk(json.loads(text))
        library=(project/'ignition/script-python/home_scada/code.py').read_text()
        self.assertNotIn('writeBlocking',library); self.assertNotIn('math.sin',library)
        for path in project.rglob('resource.json'):
            data=json.loads(path.read_text()); datetime.datetime.strptime(data['attributes']['lastModification']['timestamp'],'%Y-%m-%dT%H:%M:%SZ')
            for name in data['files']: self.assertTrue((path.parent/name).exists())

if __name__=='__main__': unittest.main(verbosity=2)
