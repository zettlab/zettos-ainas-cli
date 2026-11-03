# Troubleshooting

**English** · [简体中文](../TROUBLESHOOTING.md) · [Documentation](README.md)

| Symptom | Next step |
|---|---|
| `znas: command not found` | Check `~/.local/bin` is on PATH and reopen your terminal. |
| Cannot resolve latest release | Specify `--version v0.1.7-beta.1` and check that it is published. |
| Signature or checksum failure | Stop and download official assets again. Do not disable verification. |
| Existing file/link conflict | Back up the existing binary or skills. The installer does not force overwrite. |
| Connection failure/timeout | Verify the address, port, and network in a browser, then run `auth probe`. |
| Certificate error | Use a hostname matching a trusted certificate. Do not skip verification. |
| Expired login | Try `auth refresh`; if the refresh token is missing or rejected, sign in again. |
| Permission denied | Check the NAS account's permissions. Do not automatically become administrator. |
| No AI results | Verify file browsing and keyword search, then check NAS models and indexes. |
| Agent cannot find skills | Check the chosen agent/directory, then refresh or restart the agent. |

The tested ZettOS `1.14.0-beta` issued refresh tokens valid for one second; later refresh failed with `20006`. It had no storage pools: browsing/search failed with `65000`, `60023`, or `65003`, and question retrieval returned an empty response. See [acceptance](ACCEPTANCE.md). These findings do not prove general compatibility. Storage setup should follow the official workflow, not an unreviewed formatting command.

## Collect a minimal report

From a downloaded checkout:

```bash
python3 scripts/diagnose.py --binary znas
```

The script prints OS/architecture and Python, OpenSSL, and CLI versions. It does not read credentials or NAS content, access the network, or upload reports. Check connectivity separately with `znas --base-url '<address>' auth probe` and remove the address before posting.

Include CLI version, OS/CPU, NAS firmware, reproduction steps, a short error summary, and whether the probe succeeded. Remove passwords, tokens, usernames, serials, private file paths, and share links. Use [support](../../SUPPORT.md) for ordinary problems and [private security reporting](SECURITY.md) for authorization failures or credential/data exposure.
