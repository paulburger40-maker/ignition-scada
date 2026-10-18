# House SCADA sharing

Local operator interface: http://localhost:8088/data/perspective/client/home_scada

This computer's current Wi-Fi address is 192.168.68.179/24. DHCP may change it. The Wi-Fi profile is Public; it has not been changed. No new LAN firewall rule or router port forwarding has been enabled.

## Access design

- HomeViewer: authenticated readings/screens only.
- HomeOperator: authenticated household controls. Current controls remain simulations.
- Administrator: retains project control access; reserve Gateway administrator accounts for administration.
- All shared access must require login. Guest means an invited named viewer account, not anonymous access.
- Button visibility/disablement is backed by a Gateway script check against the actual Perspective session's security levels.
- Tailscale private-network HTTPS is the intended shared entry point for both home Wi-Fi and away-from-home devices. This avoids transmitting login passwords over plain LAN HTTP. Its HTTPS hostname is available only after the user signs in and enables HTTPS for their private network.
- No Funnel/public internet exposure, exit node or LAN subnet advertising is needed.

## Pending account commissioning

The existing `default` Ignition identity provider remains the authentication source. In Gateway administration, create named household users and add either HomeViewer or HomeOperator to their roles. Do not give guests Gateway Administrator permissions. Set passwords directly in Ignition; never place them in this workspace or source files.

The Gateway computer is now signed into Tailscale, and its private HTTPS Serve endpoint is active. User must log into Tailscale on invited phones/computers. Restrict the Tailscale network policy to approved users/devices and the HTTPS service before invitations. Tailscale's device-sharing permission does not replace Ignition's HomeViewer/HomeOperator checks.

Suggested persistent private HTTPS command after authentication and role checks pass:

`"C:\Program Files\Tailscale\tailscale.exe" serve --bg --https=443 http://127.0.0.1:8088`

This reverse proxy serves the Gateway, including its normal protected administration routes. Roles and logins must be verified first; do not distribute an administrator account. Verify Perspective WebSocket updates and IdP redirects through the resulting HTTPS hostname before sharing.

Tailscale installation and the before-sharing Gateway backup have completed. The deployed home project now rejects anonymous access and redirects to the default IdP login, with no dashboard visible. Tailscale Serve is active and tailnet-only at https://home-scada.tail78dd75.ts.net/data/perspective/client/home_scada. A fresh browser accepted its certificate without bypasses and stayed on HTTPS through the login redirect; evidence is https-anonymous-verification.json. Role-specific signed-in behavior and phone access remain to be exercised. This local HTTPS check does not prove connectivity from another device. Final verification needs a phone on home Wi-Fi and a phone on mobile data with Tailscale connected.

## Reuse and backups

`home-scada/home_scada-project.zip` exports the project resources only. Gateway backups also contain configuration and must be kept private. Historical data needs its own database backup. Never publish the workspace or Gateway backups as a way of sharing the live interface.

Sources:
- https://docs.inductiveautomation.com/docs/8.3/ignition-modules/perspective/security-in-perspective
- https://docs.inductiveautomation.com/docs/8.3/appendix/scripting-functions/system-perspective/system-perspective-isAuthorized
- https://docs.inductiveautomation.com/docs/8.3/tutorials/tutorials-and-helpful-tricks/accessing-projects-remotely
- https://tailscale.com/docs/install/windows/msi
- https://tailscale.com/docs/reference/tailscale-cli/serve
