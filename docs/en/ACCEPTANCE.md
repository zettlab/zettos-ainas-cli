# Release acceptance record

**English** · [简体中文](../ACCEPTANCE.md) · [Documentation](README.md)

Target: `v0.1.7-beta.1`. Two signed Linux candidates are attached to a draft. **Public Release gates are not satisfied.**

| Requirement | Evidence / status |
|---|---|
| Separate distribution without private Rust source/history | Established; content scan required before publication |
| Public repository and anonymous access | Repository public; README/bootstrap fetched anonymously with HTTPS 200 |
| Install, update, rollback, uninstall | 13 installer/package tests passed; actual signed x86_64 install, repeat install, and uninstall passed |
| Reject invalid signatures, digests, and unsafe archives | Installer tests passed |
| Recovery, install locking, preserve existing files | Installer tests passed |
| Password input and credential permissions | Implemented; isolated auth/permissions/concurrency/cleanup checks passed |
| Linux x86_64 | Native Ubuntu 24.04 signed candidate passed; glibc symbol requirement 2.34, older systems untested |
| Linux ARM64 | Native Ubuntu 24.04 ARM64 signed candidate passed; older systems untested |
| macOS Apple Silicon | Build, signing, and target-OS validation pending |
| NAS login, browsing, search, question retrieval | D6 Ultra / ZettOS 1.14.0-beta: login/device/firmware/storage reads passed; no storage pools; file/search/QA failed, prepared test NAS required |
| Refresh, expiration, ordinary-user permissions | Immediate refresh passed; token expires in 1 second, later refresh returns 20006; upstream confirmation and ordinary-user acceptance pending |
| Module writes and cleanup | Disposable-data scenarios pending; no destructive shared-machine tests |
| High-risk operation guards | Explicit acknowledgment and dynamic execution protections implemented; unit and actual-binary rejection checks passed |
| Dependency licensing and advisories | Notices/inventory for 187 target dependencies, MPL sources and Rust runtime notices packaged; no unhandled audit findings, bounded RSA exception in security guide |
| Documentation, privacy, licensing, support | Bilingual documentation added; final behavior review and runtime localization incomplete |
| CI and release gates | Public tools passed on three platforms; actual Linux binaries passed on two, Mac binary pending |

Evidence: [three-platform tools CI](https://github.com/zettlab/zettos-ainas-cli/actions/runs/41553493703), [native Linux CI](https://github.com/zettlab/zettos-ainas-cli/actions/runs/41553772658), [x86_64 record](../evidence/v0.1.7-beta.1/linux-x86_64.json), [ARM64 record](../evidence/v0.1.7-beta.1/linux-aarch64.json). Downloaded CI digests match the local candidate archives. Both archives' nine skills match the public repository.

Automated auth tests use isolated configuration, installer tests use temporary locations, and NAS checks use a dedicated account alias. Start with reads and restore/clean any temporary data or settings. Record unavailable devices as unverified; cross-compilation or mocked responses do not establish real-device compatibility.

The 2026-11-03 NAS check did not create, delete, or format NAS data. File spaces/list returned 65000/60023; hybrid search returned 65000/65003; question retrieval returned empty non-JSON content. Fresh refresh tokens lasted one second: immediate refresh and subsequent device reads succeeded, later refresh was rejected. These results do not pass long-lived-login or file-feature acceptance.
