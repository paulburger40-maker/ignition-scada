# Ignition SCADA development workspace

This workspace contains an offline reference archive and a searchable SQLite database for developing Ignition SCADAs. Documentation is for the Ignition **8.3 family**, not a frozen specification for every 8.3 patch. Check each page's version notes against the installed Gateway before using an API or feature.

## Search the reference database

Run with Python 3:

```
python build_knowledge.py --search '"tag" AND "alarm"'
python build_knowledge.py --search '"Perspective" AND "binding"'
python build_knowledge.py --search '"UDT"'
python build_knowledge.py --search '"backup"'
```

`ignition_knowledge.sqlite` contains a `documents` table and an FTS5 `search` table. Each reference includes its official source URL, document family, retrieval time, local HTML path and SHA-256. `knowledge/manifest.json` records archive coverage, errors and remaining URLs. The saved HTML preserves source content; some images and scripts still require internet access.

For future Codex work, ask: **Search the local Ignition database for the relevant 8.3 documentation, cite sources, then create the SCADA resources in this workspace. Check installed-version compatibility and distinguish tested resources from proposed resources.**

## Development workflow

1. Define the process: equipment, measured variables, units, normal ranges, operating states and operator actions.
2. Complete an I/O register with device addresses, data types, scaling and quality behavior. Start with simulation until device connections are explicitly authorized.
3. Design equipment UDTs and tag folders. Keep engineering units, alarm definitions and history settings consistent.
4. Build a small reusable Perspective view for one equipment type. Add overview, detail, trends and alarm views as requirements demand.
5. Use named queries with parameters for database access. Define history retention and sampling explicitly.
6. Assign operator permissions and audit required actions. Keep passwords and connection secrets outside project references and this database.
7. Verify bad quality, stale data, reconnect behavior, alarm transitions, acknowledgement, history retrieval and operator permissions.
8. Export project resources and a Gateway backup, then test restoring to a separate development Gateway before production deployment.

## Current machine

On 9 October 2026, the Windows 11 x64 laptop had approximately 23.3 GiB of visible RAM. The existing sample Gateway was upgraded from 8.3.2 to **8.3.10**, with supported backups preserved. Ignition's service is running at `http://localhost:8088`; installed core version is `8.3.10.2026100610`. **Designer Launcher 1.3.10** is installed for the current user.

The `samplequickstart` Perspective project responds over HTTP. Its device uses the programmable simulator; its SQLite historian is recording current readings, and its alarm journal initialized and contains post-upgrade events. Account/licensing verification, interactive Designer/screen tests, alarm acknowledgement and isolated restore testing remain pending because browser/computer-control tools still fail at startup.

Use `Open-Gateway.url`, `Open-Sample-SCADA.url` and `Open-Designer.url` to open the prepared local targets. The Designer link uses the documented local HTTP deep-link option and requires your Gateway login.

Official download metadata identified **8.3.10**, released 6 October 2026, as stable. Software downloads are in `software`; inspect the verification record before running an installer. No upgrade is complete merely because an installer has downloaded. Preserve the existing Gateway through a supported backup before any upgrade.

## Official resources

- [Manual](https://docs.inductiveautomation.com/docs/8.3/intro)
- [Installation guide](https://docs.inductiveautomation.com/docs/8.3/getting-started/startup-guide/downloading-and-installing-ignition)
- [Software downloads](https://inductiveautomation.com/downloads/ignition/)
- [Inductive University](https://inductiveuniversity.com/)
- [Ignition Exchange](https://inductiveautomation.com/exchange/)

This archive is for local reference. Source documentation remains the property of its publisher; check resource-specific licensing before redistributing examples or templates.
