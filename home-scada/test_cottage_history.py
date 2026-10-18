"""Real-data history behavior using isolated SQLite; never calls live equipment."""
import importlib.util,json,sqlite3,sys,types,unittest
from pathlib import Path
HERE=Path(__file__).parent
def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/'src'/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
energy=load('cottage_energy')

class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.conn=sqlite3.connect(':memory:',isolation_level=None);self.conn.row_factory=sqlite3.Row
        self.model=load('cottage_history');self.model.cottage_energy=energy
        def update(sql,args,database,**kw):return self.conn.execute(sql,args).rowcount
        def query(sql,args,database,**kw):return self.conn.execute(sql,args).fetchall()
        self.model.system=types.SimpleNamespace(db=types.SimpleNamespace(runPrepUpdate=update,runPrepQuery=query,
            beginTransaction=lambda db:self.conn.execute('BEGIN') or 'tx',commitTransaction=lambda tx:self.conn.execute('COMMIT'),
            rollbackTransaction=lambda tx:self.conn.execute('ROLLBACK'),closeTransaction=lambda tx:None),util=types.SimpleNamespace(getGlobals=lambda:{}))
        self.now=energy.parse_utc('2026-10-17T16:00:00Z')
    def tearDown(self):self.conn.close()
    def sample(self,ts,power=1000):
        self.model.record_sample(dict(online=True,updated_ms=ts,power_w=power,power_kw=power/1000,voltage_v=230,current_a=4.35))
    def test_correct_energy_and_duplicate_suppression(self):
        self.sample(self.now);self.sample(self.now+5000);self.sample(self.now+5000)
        rows=self.conn.execute('SELECT SUM(kwh),SUM(covered_ms) FROM minute_energy').fetchone()
        self.assertAlmostEqual(rows[0],1000*5/3600000);self.assertEqual(rows[1],5000)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM power_samples').fetchone()[0],2)
    def test_outage_is_not_integrated(self):
        self.sample(self.now);self.sample(self.now+30000)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM minute_energy').fetchone()[0],0)
    def test_midnight_split_follows_south_africa(self):
        midnight=energy.parse_utc('2026-10-17T22:00:00Z')
        self.sample(midnight-2500);self.sample(midnight+2500)
        rows=self.model._aggregate(midnight+5000,False)
        self.assertEqual([r['period'] for r in rows],['2026-10-17','2026-10-18'])
        self.assertEqual([r['covered_ms'] for r in rows],[2500,2500])
    def test_meter_history_supersedes_sample_energy_without_double_counting(self):
        hour=self.now//3600000*3600000
        self.sample(hour+5000);self.sample(hour+10000)
        self.model.store_intervals([(hour,hour+3600000,.25)])
        self.model.store_intervals([(hour,hour+3600000,.25)])
        rows=self.model._aggregate(hour+3600000,False)
        self.assertAlmostEqual(rows[0]['kwh'],.25);self.assertEqual(rows[0]['covered_ms'],3600000)
    def test_missing_periods_are_null_and_partial_is_explicit(self):
        rows=energy.bars([],self.now)
        self.assertEqual(len(rows),7);self.assertTrue(all(r['energy_kwh'] is None for r in rows))
        self.assertEqual(len(energy.bars([],self.now,True)),12)
        self.sample(self.now);self.sample(self.now+5000)
        data=self.model.snapshot(self.now+10000,dict(online=False))
        self.assertEqual(data['live'],[]);self.assertIsNotNone(data['daily'][-1]['energy_kwh'])
        self.assertEqual(data['daily'][-1]['completeness'],'In progress / partial')
    def test_history_intervals_validate_units_and_reject_overlap(self):
        a='2026-10-17T10:00:00Z';b='2026-10-17T11:00:00Z'
        records=[dict(start=a,end=b,usage=25)]
        self.assertEqual(energy.intervals(records,energy.parse_utc(a),energy.parse_utc(b))[0][2],.25)
        with self.assertRaises(ValueError):energy.intervals(records*2,energy.parse_utc(a),energy.parse_utc(b))
    def test_one_overview_three_charts_and_authentication_preserved(self):
        project=HERE/'overview-project'
        views=list(project.rglob('view.json'));self.assertEqual(len(views),1)
        text=views[0].read_text(encoding='utf-8');self.assertEqual(text.count('"type": "ia.chart.xy"'),3)
        for unwanted in ['EV Charging','Set up instrument','Connect meter','Tapo','Alexa','SIMULATION']:
            self.assertNotIn(unwanted,text)
        for relative in ['ignition/global-props/data.bin','com.inductiveautomation.perspective/session-permissions/data.bin']:
            self.assertEqual((project/relative).read_bytes(),(HERE/'project'/relative).read_bytes())

if __name__=='__main__':unittest.main(verbosity=2)
