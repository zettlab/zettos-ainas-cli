# Connect your first NAS

**English** · [简体中文](../QUICKSTART.md) · [Documentation](README.md)

1. Complete NAS initialization, account setup, and storage setup in the official Zettlab interface. See the [Zettlab Wiki](https://wiki.zettlab.com/).
2. Open the NAS interface in a browser on the computer running your agent. Note the working address and port. Start on the same local network.
3. After installation, check connectivity and sign in:

```bash
znas --base-url 'http://<NAS-address>:<port>' auth probe
znas --base-url 'http://<NAS-address>:<port>' auth login --username '<username>' --keep-logged-in
znas auth status
```

Login uses a hidden terminal password prompt. Do not paste passwords into chat or command arguments. For automation, a password manager can pipe one password line to `auth login --password-stdin`; do not hardcode it in scripts.

`auth probe` checks the authentication endpoint, not every NAS service. Saved accounts are used by later commands. For multiple NAS devices, supply `--account <alias>` when logging in and the global `--account <alias>` on subsequent commands.

## Browse before searching

```bash
znas file root spaces
znas file root list --json '{"path":"/personal","size":20,"index":0}'
```

Child folders may have full storage paths in the response. Copy the returned path when navigating further. Do not guess storage-pool paths or use `/` as the initial browsing root.

Search and content questions have separate entry points:

```bash
znas search --query 'cats'
znas ask --question 'Summarize the product launch documents on my NAS'
```

AI search and question-context retrieval require corresponding NAS services, models, and indexes. If they are unavailable, check ordinary file browsing first. `znas ask` supplies retrieved context for an agent; the agent generates the answer. Returned content may reach the agent's model provider; see [privacy](PRIVACY.md).

## Remote access and permissions

Configure remote access through the official product workflow, then verify a reachable HTTPS gateway URL. An assistance code or device identifier cannot replace the URL. Do not expose local HTTP directly to the internet or bypass certificate checks. Remote connection modes still need individual acceptance; see [compatibility](COMPATIBILITY.md).

Use an ordinary NAS account for browsing and search, and administrative permissions only when needed. Confirm the target and impact before deletion, overwrite, sharing, application installation, or settings changes.

On the tested firmware, refresh tokens expired after one second. Immediate refresh succeeded, but later refresh was rejected. See [acceptance](ACCEPTANCE.md); long-lived login is not verified. If refresh is rejected, sign in again through the hidden prompt.
