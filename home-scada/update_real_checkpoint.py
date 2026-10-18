"""Record verified real-equipment state without credentials."""
from pathlib import Path
import json,zipfile,hashlib
ROOT=Path(__file__).resolve().parent.parent
HOME=ROOT/'home-scada'
for name in ('before-real-only-20261010','before-meter-auth-fix-20261011'):
    path=ROOT/'backups'/(name+'.gwbk')
    if path.exists():
        with zipfile.ZipFile(path) as z:
            report=dict(file=str(path),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),entries=len(z.infolist()),zip_error=z.testzip())
        (path.parent/(name+'-verification.json')).write_text(json.dumps(report,indent=2))
deployed=Path('C:/Program Files/Inductive Automation/Ignition/data/projects/home_scada')
source=HOME/'project'
matches=all((deployed/p.relative_to(source)).exists() and (deployed/p.relative_to(source)).read_bytes()==p.read_bytes() for p in source.rglob('*') if p.is_file())
manifest=json.loads((HOME/'build-manifest.json').read_text())
manifest.update(imported=matches,interactive_tested=False,previous_real_only_deployment_verified=True,
    native_snapshot_verified=True,previous_button_action_verified=True,
    old_home_instances_retired=(ROOT/'backups/retired-home-tags-20261010.json').exists(),live_meter_verified=False)
(HOME/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
brief='''# Home SCADA — current project brief

The user's request on 10 October 2026 to remove all demos and simulations supersedes the prototype requirements.

- Ignition 8.3.10 Maker, Perspective and LIDT Energy Monitoring; personal house project home_scada.
- Identified real meter: SONOFF POWCT cottage, eWeLink ID 10023339b5. Keep its cottage boundary distinct from whole-house measurements.
- Mode: real equipment, read-only. No generated measurements, graph points, charging/switch/security states or active physical commands.
- Seven existing page routes and an administrator-only instrument-slot form. A saved slot records identity; it does not commission hardware.
- Future slots: Geely wall charger, real smart switches, Alexa, smart TV and Tapo devices. Exact models/interfaces are required. Cottage geyser connection is deferred.
- CUBE API consent is required. The access-token request must include app_name. Code 401 means approval is required; other errors must not be described as an approval wait.
- CUBE transport resolves cube.local and confirms its VM MAC 08-00-27-D4-7F-55. Do not assume its DHCP address stays fixed.
- Accept only positively identified, fresh meter responses. Unknown/offline/stale measurements remain unavailable; verify units against eWeLink before real history or LIDT mapping.
- Home test instances were exported and retired after a supported backup. Old unused UDT definitions/history are retained outside current screens. Do not delete unrelated sample projects or historical stores.
- Existing default IdP and protected project. Administrator checks guard bridge/inventory changes. Named guest/operator provisioning and role tests remain pending. Physical controls remain disabled.
- Private Tailscale HTTPS sharing; user reported phone app login. No public exposure or router forwarding.
- Household tariff, dedicated real historian, alarms, cumulative-energy verification and LIDT mapping are pending.
- Credentials stay encrypted outside the workspace and knowledge database. No passwords/keys in inventory fields.
- Preserve supported backups and distinguish staged code from exercised native imports.
- Assistant heartbeat remains paused; credential recovery remains cancelled.
'''
(HOME/'PROJECT_BRIEF.md').write_text(brief)
(HOME/'src/home_scada.py').write_text((HOME/'src/real_home_scada.py').read_text())
checkpoint='**Latest checkpoint (11 October):** The real-equipment-only house dashboard was successfully deployed with a verified supported backup and Gateway restart. Native snapshots run; the old owned home test instances were exported and retired. Seven routes plus an instrument-slot popup have no generated values or controls. The meter button reaches its API request, but the original request omitted required app_name and mistakenly treated code 400 as pending consent. That source defect is corrected and covered by a regression check. CUBE DHCP moved from 192.168.68.198 to 192.168.68.173; the loopback relay now resolves cube.local and checks the owned VM MAC. Corrected API requests return 401 for user approval. Latest corrected project matches installed resources: '+str(matches)+'. API consent, actual device sync/identity/capability data, unit validation, real history and LIDT mapping are still unverified. Read home-scada/REAL_EQUIPMENT_STATUS.md and qa/real-runtime.json. Keep password recovery cancelled and the assistant heartbeat paused.'
path=ROOT/'SETUP_STATUS.md'; content=path.read_text(); start=content.index('**Latest'); end=content.index('\n\n',start)
path.write_text(content[:start]+checkpoint+content[end:])
path=ROOT/'software/cube-os/CONTINUATION_STATUS.md'
with path.open('a') as f:
    f.write('\n## Real-equipment update and authorization fix — latest checkpoint\n\n'+checkpoint+'\n')
print(json.dumps(dict(resources_match=matches,old_home_instances_retired=manifest['old_home_instances_retired'])))
