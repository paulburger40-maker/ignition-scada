# Reconnect the Android Perspective app

Confirmed 17 October: the same phone can sign into the house SCADA through its browser. The native app still returns Error 400 at an authentication callback. Server public HTTPS metadata and forwarded headers are verified. Do not disable authentication, certificate validation or the HTTP firewall block.

1. Keep Tailscale connected.
2. Close the failed login screen and return to the Ignition Perspective project list. Remove only the saved My Home project entry (not the server project).
3. Tap +, Gateway Search, Manually Input Gateway. Enter https://home-scada.tail78dd75.ts.net:443 (the Gateway address, without a project or login callback path).
4. Choose My Home and sign in promptly. This creates a fresh request using the corrected address. Do not bookmark an IdP login/callback URL.
5. If it still fails, record the app version and the error path. Android app Settings > Advanced Settings > View Logs provides the supported diagnostic view. Share only relevant status/error lines; omit cookies, tokens and complete authentication query strings.

Removing the app entry is a device-local operation; the laptop cannot do it without access to the phone. This reconnection has not yet been tested.

Official instructions: https://docs.inductiveautomation.com/docs/8.3/ignition-modules/perspective/perspective-sessions/ignition-perspective-app
Official diagnostics: https://support.inductiveautomation.com/hc/en-us/articles/36183777105933-Troubleshooting-the-Perspective-Mobile-App
