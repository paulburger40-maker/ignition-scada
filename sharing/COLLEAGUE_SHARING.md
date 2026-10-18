# Read-only colleague access — prepared, not enabled

The current house project is protected by Ignition login and private Tailscale access. Its address is https://home-scada.tail78dd75.ts.net/data/perspective/client/home_scada. This is not a public link.

Provision each colleague with an individual Ignition account carrying only HomeViewer. The existing project permits HomeViewer login; Gateway checks require Administrator for meter authorization and instrument configuration. Physical equipment controls are not commissioned. Do not share the owner's administrator account or passwords. Do not grant HomeOperator or Administrator to colleagues.

Allow approved colleagues to reach only the SCADA host over Tailscale. Do not invite colleagues to the whole home network or grant access to the CUBE setup port 8443. Their names/account identifiers and the final access scope are needed before granting access. No invitations have been sent and no colleague accounts have been created.

Before distributing the link, verify with a real HomeViewer session that project login works, Connect meter and instrument setup are disabled, and no configuration or device command can be invoked. Decide whether the audience may see the actual cottage electrical readings. A project export is a design artifact rather than a running remote service; never distribute full Gateway backups, private keys or API credentials.

Maker Edition is for the personal house project. Commercial mining deployments require appropriate commercial licensing; no purchases are authorized by this preparation.

# Operation with the laptop off

Ignition, history storage, CUBE OS and the network relay currently run on this laptop. They cannot serve the SCADA after this host is shut down. Tailscale does not keep a shut-down Gateway running.

Continuous operation requires an always-on host such as a spare computer or suitable server/NAS. A supported migration must preserve the Ignition version, permitted licence, house project, identity configuration, verified real historian and CUBE integration. API credentials must remain encrypted on the target or be reauthorized there. Device interfaces and private network access must be tested before retiring the laptop deployment. Do not restore an entire Gateway backup onto a machine with unrelated active equipment connections.

No cloud service, subscription, hardware purchase, external account or permanent hosting has been created. The assistant schedule remains paused.
