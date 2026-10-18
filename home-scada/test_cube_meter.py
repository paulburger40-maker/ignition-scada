"""Meaningful decoder/identity checks; no live device or API credentials used."""
import importlib.util,math,unittest,types
from pathlib import Path
spec=importlib.util.spec_from_file_location('cube_model',Path(__file__).parent/'src/cube_meter.py')
model=importlib.util.module_from_spec(spec); spec.loader.exec_module(model)

def meter(**changes):
    d=dict(serial_number='cube-serial',tags={'ewelink':{'deviceid':'10023339b5'}},online=True,
        capabilities=[{'capability':x} for x in ('electric-power','voltage','electric-current')],
        state={'electric-power':{'electric-power':7061},'voltage':{'voltage':23015},'electric-current':{'electric-current':31}},firmware_version='unverified-test')
    d.update(changes); return d

class DecoderChecks(unittest.TestCase):
    def test_history_query_cannot_send_equipment_commands(self):
        previous_get=model._get;previous_system=getattr(model,'system',None)
        spec=importlib.util.spec_from_file_location('cottage_energy',Path(__file__).parent/'src/cottage_energy.py')
        helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);model.cottage_energy=helper
        calls=[]
        class Secret:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def getSecretAsString(self):return 'isolated-test-placeholder'
        data=meter(serial_number=model.CUBE_SERIAL,third_serial_number=model.BUILTIN_DEVICE_ID)
        data['capabilities'].append({'capability':'power-consumption','settings':{'resolution':{'value':3600}}})
        response=types.SimpleNamespace(statusCode=200,json={'error':0,'data':{'electricityIntervals':[{'start':'2026-10-17T10:00:00Z','end':'2026-10-17T11:00:00Z','usage':25}]}})
        client=types.SimpleNamespace(post=lambda url,**kw:calls.append((url,kw)) or response)
        try:
            model._get=lambda endpoint,token:{'error':0,'data':{'device_list':[data]}}
            model.system=types.SimpleNamespace(util=types.SimpleNamespace(jsonDecode=lambda value:{}),file=types.SimpleNamespace(readFileAsString=lambda path:'{}'),
                secrets=types.SimpleNamespace(decrypt=lambda value:Secret()),net=types.SimpleNamespace(httpClient=lambda **kw:client))
            rows,resolution=model.query_consumption(helper.parse_utc('2026-10-17T10:00:00Z'),helper.parse_utc('2026-10-17T11:00:00Z'))
            self.assertEqual(len(rows),1);self.assertEqual(resolution,3600)
            self.assertTrue(calls[0][0].endswith('/'+model.CUBE_SERIAL+'/query-state/power-consumption'))
            state=calls[0][1]['data']['query_state']
            self.assertEqual(set(state),{'power-consumption'})
            self.assertEqual(set(state['power-consumption']),{'type','timeRange'})
            self.assertEqual(state['power-consumption']['type'],'summarize')
        finally:
            model._get=previous_get
            if previous_system is None:del model.system
            else:model.system=previous_system
    def test_api_request_identifies_application_and_never_uses_write_method(self):
        calls=[]
        client=types.SimpleNamespace(get=lambda url,**kw:calls.append((url,kw)) or types.SimpleNamespace(statusCode=200,json={'error':401}))
        previous=model._client
        try:
            model._client=client
            model._get('bridge/access_token')
            self.assertEqual(calls[0][1]['params']['app_name'],'Ignition Home SCADA')
            self.assertNotIn('Authorization',calls[0][1]['headers'])
            with self.assertRaises(ValueError): model._get('devices/relay')
            self.assertEqual(len(calls),1)
        finally: model._client=previous
    def test_electrical_unit_conversion(self):
        r=model.decode_meter(meter()); self.assertAlmostEqual(r['power_w'],70.61)
        self.assertAlmostEqual(r['power_kw'],.07061); self.assertAlmostEqual(r['voltage_v'],230.15)
        self.assertAlmostEqual(r['current_a'],.31)
        self.assertIsNone(r['total_kwh']); self.assertIsNone(r['today_kwh'])
    def test_wrong_and_duplicate_meter_are_rejected(self):
        for devices in ([meter(tags={})],[meter(),meter()]):
            with self.assertRaises(ValueError): model.select_meter({'error':0,'data':{'device_list':devices}})
    def test_original_id_in_official_third_party_serial_field(self):
        d=meter(tags={},third_serial_number='10023339b5')
        self.assertIs(model.select_meter({'error':0,'data':{'device_list':[d]}}),d)
        d['third_serial_number']='10023339b5_built_in'
        self.assertIs(model.select_meter({'error':0,'data':{'device_list':[d]}}),d)
        d['third_serial_number']='10023339b5_unrecognized_suffix'
        with self.assertRaises(ValueError): model.select_meter({'error':0,'data':{'device_list':[d]}})
        d['third_serial_number']='another-device'
        with self.assertRaises(ValueError): model.select_meter({'error':0,'data':{'device_list':[d]}})
    def test_offline_never_shows_cached_values(self):
        r=model.decode_meter(meter(online=False)); self.assertIsNone(r['power_w']); self.assertFalse(r['online'])
    def test_relay_state_is_not_watts(self):
        r=model.decode_meter(meter(capabilities=[{'capability':'power'}],state={'power':{'powerState':'on'}}))
        self.assertIsNone(r['power_w']); self.assertFalse(r['online'])
    def test_invalid_measurements_are_rejected(self):
        for value in (True,float('nan'),float('inf'),-100):
            with self.assertRaises(ValueError): model.decode_meter(meter(state={'electric-power':{'electric-power':value}}))
    def test_nested_device_identity(self):
        d=meter(); self.assertIs(model.select_meter({'error':0,'data':{'device_list':[d]}}),d)

if __name__=='__main__': unittest.main(verbosity=2)
