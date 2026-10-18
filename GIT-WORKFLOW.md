# Private Ignition source workflow

Repository: https://github.com/paulburger40-maker/ignition-scada (private).

This folder remains the active source workspace used by the existing SCADA chat. It now has independent Git history. Read AGENTS.md, SETUP_STATUS.md and home-scada/PROJECT_BRIEF.md before changes. Generated project resources are staged source; only runtime verification establishes that they have been imported and exercised.

Git includes authored home-scada source and reviewed resource JSON, templates, setup notes, and selected sharing/deployment scripts. It excludes full Gateway backups, credentials, runtime databases, downloaded installers/manuals, logs, browser automation and QA captures. Those files are preserved locally. Use Backup-Ignition.ps1 and the supported Gateway export procedure for recovery backups; Git cannot restore credentials or live history by itself.

Create codex/ branches for substantial work and commit stable checkpoints. Use the manager's Save-Project command or ask Codex to review and save a private checkpoint. A Git push never authorizes a Gateway deployment or physical equipment commands. Preserve the real-equipment, read-only requirements in the current project brief.