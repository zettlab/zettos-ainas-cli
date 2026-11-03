# Compatibility and support scope

**English** · [简体中文](../COMPATIBILITY.md) · [Documentation](README.md)

This is the acceptance scope for the first public Beta. **Compilation, available routes, and documentation are not evidence of successful real-device validation.** Published assets and accepted platforms are defined by release evidence.

| Client platform | Planned asset | Current evidence |
|---|---|---|
| Linux x86_64 | `znas-linux-x86_64.tar.gz` | Signed candidate passed on native Ubuntu 24.04; glibc symbol requirement 2.34, older systems untested |
| Linux ARM64 | `znas-linux-aarch64.tar.gz` | Signed candidate passed on native Ubuntu 24.04 ARM64; older systems untested |
| macOS Apple Silicon | `znas-macos-aarch64.tar.gz` | Build, minimum OS, signing, and execution still pending |
| Windows / Intel Mac | None | Unsupported; no WSL or Rosetta compatibility promise |

A Zettlab D6 Ultra reporting ZettOS `1.14.0-beta` passed login and device, firmware, and storage reads. That environment had no storage pools: file browsing, search, and question retrieval did not pass. Refresh tokens lasted one second, so long-lived login remains unverified. See [acceptance](ACCEPTANCE.md). We do not claim all ZettOS versions work or substitute internal service branch names for firmware versions. Device serials, addresses, and account names are excluded from public evidence.

| Capability | Prerequisites | Required acceptance |
|---|---|---|
| Login and browsing | Reachable gateway, NAS account, usable storage | Login, refresh, expiration, ordinary-user permissions |
| Search and question retrieval | File access, AI services/models/indexes | Search, unavailable-AI behavior, question context |
| Settings and desktop status | Corresponding services; admin for some tasks | Read scenarios; writes tested separately by risk |
| Applications and containers | Services and suitable storage | Experimental; install/start/cleanup scenarios pending |
| Photos | Photos service and index | Experimental; user scenarios pending |
| Coder and Theater | Installed applications and gateway routes | Experimental; user scenarios pending |
| Remote access | Official setup and reachable HTTPS gateway | Verify each connection mode individually |

For `404`, unavailable services, or permission errors, check firmware and application versions. The CLI does not substitute native host commands for NAS APIs. If the binary needs a newer glibc than the host provides, installation preflight fails and preserves the old version. Do not replace system glibc to install this CLI.
