# Platform and feature requirements

**English** · [简体中文](../COMPATIBILITY.md) · [Documentation](README.md)

**No version is available for download yet.** Available platform assets, minimum OS versions, and supported NAS firmware are defined by the corresponding published Release notes.

| Computer platform | Download plan |
|---|---|
| Linux x86_64 | `znas-linux-x86_64.tar.gz` planned |
| Linux ARM64 | `znas-linux-aarch64.tar.gz` planned |
| macOS Apple Silicon | `znas-macos-aarch64.tar.gz` planned |
| Windows / Intel Mac | Not offered; no WSL or Rosetta compatibility promise |

Installation requires Python 3.9+, curl, and OpenSSL. Install the CLI on the computer running your terminal or agent. It connects through the NAS gateway and does not require NAS SSH access.

| Feature | Requirements |
|---|---|
| Login and file browsing | Reachable gateway, NAS account, configured storage, file permissions |
| Search and content questions | File permissions; AI features also require NAS services, models, and content indexes |
| Device settings and desktop status | Corresponding NAS services; administrator permissions for some operations |
| Applications and containers | Corresponding services and available storage |
| Photos | Photos application and index |
| Coder and Theater | Installed applications accessible through the gateway |
| Remote connections | Official remote-access setup and a reachable HTTPS gateway URL |

Features may differ between firmware and application versions. A successful `auth probe` confirms the authentication endpoint, not every feature. For `404`, unavailable services, or permission errors, check firmware, application versions, and account permissions. See [troubleshooting](TROUBLESHOOTING.md).

The CLI does not substitute native host commands for NAS control APIs. If the host does not meet a Linux binary's glibc requirement, installation preflight fails and preserves the old version. Do not replace system glibc to install the CLI.
