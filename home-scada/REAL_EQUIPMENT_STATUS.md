# Live meter checkpoint — 17 October 2026

Real native readings now update in `qa/meter-runtime.json`: SONOFF POWCT cottage, exact original ID 10023339b5_built_in, firmware 1.3.1. Typical observed values during commissioning were 1.56–1.72 kW, 222–223 V and 14 A. These are measurements at that time, not constants or whole-house totals. No relay commands exist. Source scaling is the official CUBE V2 0.01 W/V/A contract; independent app comparison is pending. kWh counters, historian, tariff and LIDT mapping are still unavailable.

The native startup event is imported and exercised: polling starts after Gateway restart without an open Perspective view. The diagnostic snapshot contains only whitelisted device identity and measurements, never tokens or request headers. Supported backups before-phone-fix-20261017.gwbk and before-meter-identity-20261017.gwbk passed ZIP integrity and SHA-256 checks. Only the house project reader/startup and approved web settings were changed. Existing view content/permissions remain deployed; regenerated metadata for other staged resources is not evidence of a new native import.

Phone HTTPS metadata is repaired, but the real phone still reports Error 400. Sharing access and phone operation remain incomplete. See ../sharing/phone-server-verification-20261017.json and SETUP_STATUS.md.

## Historical commissioning notes

# My Home — real equipment

The active native Ignition project shows real equipment and instrument slots only. It generates no electrical readings, switch states, charging states, security states or trends. The earlier prototype is archived in `archive/simulation-base-20261010.zip`; the default build now creates the real-equipment project.

Open [Home SCADA](https://home-scada.tail78dd75.ts.net/data/perspective/client/home_scada). The seven pages retain their previous URLs. Energy and Overview include the identified SONOFF POWCT cottage meter. Unavailable readings are explicit; the cottage meter does not stand in for whole-house measurements.

An administrator can click **Connect meter**, then approve the API-access request in [CUBE on the home network](http://cube.local/). The reader waits for approval for two minutes and displays a visible outcome. It accepts only device ID `10023339b5`, queries read-only endpoints, discards offline/stale readings, and stores the API credential encrypted outside this workspace. Compare actual readings and unit scaling with eWeLink before commissioning history or LIDT mapping. Daily/monthly/reset counters are not lifetime energy totals.

The **Instruments** page and category pages provide instrument-slot forms. These store a name, type, model and location. A saved slot remains **Not connected** until its adapter and telemetry are commissioned. No relay, EV charging, television, Alexa or security commands are active. Administrator permission is checked again in the Gateway before configuration.

Geely wallbox, smart switches, Alexa, TV and Tapo areas have no fabricated values. Exact models and supported interfaces are required. The geyser switch connection remains deferred. Household tariff, real history, alarms and LIDT mappings remain to be commissioned.

The owned previous home test instances were exported and retired after `backups/before-real-only-20261010.gwbk` was created. Older history stays in the sample database and is excluded from this interface. Unused old UDT definitions are retained; they generate no values. Other Gateway projects and devices were not changed.

Build with `python build_home_scada.py`. `build-manifest.json` distinguishes import from interactive verification. `qa/real-runtime.json` contains nonsecret Gateway runtime evidence. The relay and CUBE VM still need automatic-startup configuration before unattended operation; the assistant heartbeat remains paused.

References: [Perspective authorization](https://docs.inductiveautomation.com/docs/8.3/appendix/scripting-functions/system-perspective/system-perspective-isAuthorized), [HTTP client](https://docs.inductiveautomation.com/docs/8.3/appendix/scripting-functions/system-net/system-net-httpClient), [Secrets encryption](https://docs.inductiveautomation.com/docs/8.3/appendix/scripting-functions/system-secrets/system-secrets-encrypt), [CUBE API](https://ewelink.cc/ewelink-cube/introduce-open-api/document/).
