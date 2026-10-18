# Ignition access recovery (prepared; not started)

**Cancelled on 10 October 2026:** the user recovered the password and reported successful application login. Do not run recovery from an old approval. A fresh explicit request is required; recovery-cancelled.flag blocks the helper.

The user cannot remember the existing Ignition password and requested retrieval. The original plaintext is unavailable from a stored one-way hash; no password-manager or credential-vault extraction is performed.

The official 8.3 recovery operation `gwcmd -p` does not merely change the existing password. After a Gateway restart it starts partial commissioning and lets the user create a temporary administrator. This changes the Gateway's authentication configuration, so explicit recovery approval is requested before invoking it.

Prepared helper: Recover-Gateway-Access.cmd. It requires Windows administrator approval, saves a supported Gateway backup, requests the official password-recovery operation, and restarts the Gateway. It never logs or stores new passwords. Existing projects remain in place.

After approval and helper completion:

1. Open the Gateway at its private HTTPS root and complete recovery commissioning, entering a new temporary administrator username/password directly in Ignition.
2. Sign in to Gateway administration using that temporary administrator.
3. In the existing default user source, change the password of the original owner account. The house project explicitly uses the default IdP; the temporary Gateway account alone is not a house-project login.
4. Verify the original account can sign into the house project through its HTTPS URL.
5. Restore the original Gateway security settings. The documented recovery changes the System Identity Provider, Designer Authentication Strategy, System User Source and Designer/Gateway read/write permissions. Preserve the original values before applying recovery.
6. After the restored owner login and permissions pass, remove the temporary recovery user source and IdP through supported Gateway administration. Do not leave temporary access in place or restore a full old backup merely to clean up authentication.

No external guests are currently invited. The Tailscale private network currently has the Gateway computer and the user's own Android phone. Do not invite others or share administrative credentials during recovery.

Source: https://docs.inductiveautomation.com/docs/8.3/platform/gateway/gateway-command-line-utility-gwcmd
