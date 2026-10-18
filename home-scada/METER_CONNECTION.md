# POWCT cottage commissioning

The user provided an eWeLink device-sharing invitation (EU region) and a screenshot named POWCT cottage. The physical label in the supplied photographs confirms SONOFF POWCT. Firmware, device ID and the connection capability of this unit remain unconfirmed. The geyser switch was deferred at the user's request.

The screenshot shows power in W and day/month energy in kWh. These are reference observations, not live data; no screenshot numbers are imported into tags or historian. A cottage meter is not assumed to measure the whole house.

## Required information

1. eWeLink Device information: model, firmware version and whether LAN Control exists.
   The model is now confirmed from the hardware label; Device ID and firmware are still needed.
2. Confirm the circuit boundary and whether the meter measures import only or supports a verified export reading.
3. Identify an existing CUBE OS/iHost or other authorized integration host, or choose a documented cloud integration after checking availability and costs. An app sharing invitation is not a persistent API token.
4. Verify device ownership/access, live API field names, units, scaling, timing and energy counter reset behavior.

The current official eWeLink CUBE route syncs supported account devices into a CUBE host and exposes a documented local API. Support depends on the exact device/firmware. Shared devices may have different availability than devices owned by that account. No CUBE host is currently confirmed, and no cloud account or token has been accessed.

## Commissioning behavior

- Read-only initial integration. Do not switch the meter's relay; on POWCT that output can operate an external contactor.
- Use [default]HomeSCADAReal/Meters/POWCTCottage, separate from simulation paths.
- Retain source timestamps and communication quality. A stale/disconnected meter must show unavailable/stale, not 0 W.
- Convert verified W to kW by dividing by 1000 for LIDT power mapping.
- Today/month values reset periodically. Never map them directly as a lifetime cumulative energy totaliser for LIDT.
- If the API supplies a verified cumulative kWh total, use it with documented reset/rollover handling. Otherwise choose a clearly labelled calculated energy method and validate it against the meter; do not imply billing accuracy.
- Select a dedicated physical-data historian before recording readings.
- First verify power/day/month values against the eWeLink screen while a normal household load changes. Check disconnect/reconnect and date rollover. No load switching is authorized by read-only commissioning.

## Sources

- https://sonoff.tech/products/sonoff-pow-ring-smart-power-meter-powct
- https://cube.ewelink.cc/getting-started/add-devices/ewelink-wi-fi-devices
- https://ewelink.cc/ewelink-cube/add-on/ewelink-smart-home/
- https://ewelink.cc/ewelink-cube/introduce-open-api/document/

Retrieved/reviewed 2026-10-10. The user's invitation token and credentials are not stored in these files or the knowledge database.

User app screenshots positively match POWCT cottage to Device ID 10023339b5 at 192.168.68.107:8081, with LAN control enabled. MAC C4:D8:D5:B5:13:30 and firmware name SN-ESP32D0-POWCT-01 are recorded. The app showed current firmware 1.1.1 and update 1.3.1; the user updated it and reported completion, and read-only discovery confirmed its return after restart. Post-update firmware version is not yet read. No device commands or encrypted payloads were saved. Evidence: qa/ewelink-discovery.json. Device 1001720bbe is outside the current meter integration scope.

The official CUBE OS 2.14.1 installer and its VirtualBox dependency are downloaded and verified. Bridge runtime installation is pending Windows approval; no VM, account login, device synchronization or API token exists yet. See ../software/cube-os/SETUP.md. The meter must continue to show unavailable until actual authorized measurements are verified.
