"""Exercise exported navigation actions with the Gateway API contract."""
import json,unittest,types
from pathlib import Path
ROOT=Path(__file__).parent/'project/com.inductiveautomation.perspective/views/Home'

def buttons(value):
    if isinstance(value,dict):
        if value.get('type')=='ia.input.button': yield value
        for child in value.values(): yield from buttons(child)
    elif isinstance(value,list):
        for child in value: yield from buttons(child)

def run(button,perspective):
    feedback=types.SimpleNamespace(actionFeedback='')
    component=types.SimpleNamespace(view=types.SimpleNamespace(custom=feedback),
        session=types.SimpleNamespace(props=types.SimpleNamespace(id='this-session')),
        page=types.SimpleNamespace(props=types.SimpleNamespace(pageId='this-page')))
    messages=[]
    system=types.SimpleNamespace(perspective=perspective,util=types.SimpleNamespace(
        getLogger=lambda name:types.SimpleNamespace(warn=messages.append)))
    namespace={'system':system}
    script=button['events']['component']['onActionPerformed']['config']['script']
    exec(compile('def runAction(self,event):\n'+script,'exported-action','exec'),namespace)
    namespace['runAction'](component,None)
    return feedback,messages

class ActionTests(unittest.TestCase):
    def test_navigation_targets_the_originating_session_and_page(self):
        count=0
        for path in ROOT.rglob('view.json'):
            for button in buttons(json.loads(path.read_text(encoding='utf-8'))):
                if not button['meta']['name'].startswith('Nav'):continue
                calls=[]
                run(button,types.SimpleNamespace(navigate=lambda **kw:calls.append(kw)))
                self.assertEqual(len(calls),1)
                self.assertEqual(calls[0]['sessionId'],'this-session')
                self.assertEqual(calls[0]['pageId'],'this-page')
                self.assertTrue(calls[0]['page'].startswith('/'));count+=1
        self.assertEqual(count,49)

    def test_popup_is_targeted_and_fits_phone_viewport(self):
        view=json.loads((ROOT/'Integrations/view.json').read_text(encoding='utf-8'))
        button=next(b for b in buttons(view) if b['meta']['name']=='AddOther')
        calls=[]
        run(button,types.SimpleNamespace(openPopup=lambda *args,**kw:calls.append((args,kw))))
        self.assertEqual(calls[0][1]['sessionId'],'this-session')
        self.assertEqual(calls[0][1]['pageId'],'this-page')
        self.assertTrue(calls[0][1]['viewportBound'])

    def test_navigation_failure_produces_visible_feedback(self):
        view=json.loads((ROOT/'Energy/view.json').read_text(encoding='utf-8'))
        button=next(b for b in buttons(view) if b['meta']['name']=='Nav0')
        def fail(**kw):raise RuntimeError('test failure')
        feedback,messages=run(button,types.SimpleNamespace(navigate=fail))
        self.assertIn('Action failed',feedback.actionFeedback)
        self.assertEqual(messages,['Nav0 failed: RuntimeError'])
        self.assertIn('ActionFeedback',json.dumps(view))

if __name__=='__main__':unittest.main(verbosity=2)
