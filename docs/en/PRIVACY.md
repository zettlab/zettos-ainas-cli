# Privacy and data flow

**English** · [简体中文](../../PRIVACY.md) · [Documentation](README.md)

`znas` calls NAS services through the configured gateway and account. The NAS enforces account permissions. Password input is hidden in the terminal, and login encrypts the password with the NAS-provided public key. Use HTTPS over public networks: password-field encryption does not replace transport security.

Access credentials are stored in your local user configuration directory: normally `~/.config/znas` on Linux and `~/Library/Application Support/znas` on macOS. `XDG_CONFIG_HOME` or `ZETTOS_NAS_CLI_CONFIG_DIR` can change this location. Encrypted credentials and the local key have restricted permissions; this does not protect them from software already running with your account's privileges.

The installer downloads scripts and Release assets from GitHub, which receives normal download-request information. The installer and diagnostic script do not proactively upload NAS content or diagnostic output.

When using an AI agent, file names, search excerpts, retrieved question context, and file content read by the agent may enter the conversation and reach its model provider. Where NAS indexing runs and where agent conversations run are separate questions. Review your agent/model privacy settings and only grant access to content you intend to share.

Third-party NAS applications, remote access, and sharing features have their own privacy settings. Removing the CLI does not retract content already sent to a model provider or disable NAS share links.

Uninstall retains saved login information by default. `uninstall --yes --purge-credentials` removes CLI accounts and the local key in the current configuration directory. Environment credentials, external files, and legacy keychain entries require separate cleanup.
