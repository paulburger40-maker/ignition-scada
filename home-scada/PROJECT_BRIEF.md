# Home SCADA — current project brief

## Current request — 17 October 2026

Replace the busy house UI with one Cottage Overview tab. Show only live cottage power (kW), voltage (V), current (A), last-24-hour power profile with a live instantaneous marker/value, daily energy for seven days, and monthly energy for twelve months. Keep the existing /energy address as an alias to the same Overview for saved links. Remove other active screens and setup slots; preserve their old resources in a backup for later expansion. Authentication and private sharing stay in force.

Persist only real readings in a dedicated local SQLite connection Home_Energy_SQLite, outside OneDrive. Compute energy between adjacent real power samples only when gaps are no more than 20 seconds; use South African day/month boundaries. Query only the positively identified POWCT historical-energy capability; validated meter intervals supersede overlapping sampled energy. Missing periods remain null, partial periods are labelled, and no invented pre-installation profile is allowed. This is a dedicated SQL history store; LIDT/native tag historian mapping is not part of this simplified UI.

## Prior scope retained for reference

The user's request on 10 October 2026 to remove all demos and simulations supersedes the prototype requirements.

- Ignition 8.3.10 Maker, Perspective and LIDT Energy Monitoring; personal house project home_scada.
- Identified real meter: SONOFF POWCT cottage, eWeLink ID 10023339b5. Keep its cottage boundary distinct from whole-house measurements.
- Mode: real equipment, read-only. No generated measurements, graph points, charging/switch/security states or active physical commands.
- Seven existing page routes and an administrator-only instrument-slot form. A saved slot records identity; it does not commission hardware.
- Future slots: Geely wall charger, real smart switches, Alexa, smart TV and Tapo devices. Exact models/interfaces are required. Cottage geyser connection is deferred.
- CUBE API consent is complete and the encrypted native credential is in use. Firmware 1.3.1 and changing power/voltage/current readings are verified. The CUBE third-party identifier is exactly 10023339b5_built_in; its internal UUID differs from the eWeLink ID. No new consent is needed for ordinary polling. The original authorization rules remain: The access-token request must include app_name. Code 401 means approval is required; other errors must not be described as an approval wait.
- CUBE transport resolves cube.local and confirms its VM MAC 08-00-27-D4-7F-55. Do not assume its DHCP address stays fixed.
- Accept only positively identified, fresh meter responses. Unknown/offline/stale measurements remain unavailable; verify units against eWeLink before real history or LIDT mapping.
- Home test instances were exported and retired after a supported backup. Old unused UDT definitions/history are retained outside current screens. Do not delete unrelated sample projects or historical stores.
- Existing default IdP and protected project. Administrator checks guard bridge/inventory changes. Named guest/operator provisioning and role tests remain pending. Physical controls remain disabled.
- Private Tailscale HTTPS settings are server-verified after Java-properties serialization repair. The user confirms the phone browser link opens the dashboard. The user now confirms the correct Ignition Perspective app works after adding the HTTPS Gateway. The user now reports Chrome works after the button update; direct automated signed-in QA is not completed. The app connection is user-verified. No public exposure or router forwarding.
- Household tariff, dedicated real historian, alarms, cumulative-energy verification and LIDT mapping are pending.
- Credentials stay encrypted outside the workspace and knowledge database. No passwords/keys in inventory fields.
- Preserve supported backups and distinguish staged code from exercised native imports.
- Assistant heartbeat remains paused; credential recovery remains cancelled.
