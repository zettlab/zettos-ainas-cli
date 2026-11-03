# Installation and version management

**English** · [简体中文](../INSTALL.md) · [Documentation](README.md)

Downloads are planned for Linux x86_64, Linux ARM64, and macOS Apple Silicon. **No version is available for download yet.** Use these commands only after the corresponding version is published. See [compatibility](COMPATIBILITY.md) for platform and system requirements.

Python 3.9+, curl, and OpenSSL must be on PATH. Rust is not required. Native Windows and Intel Mac are unsupported. On macOS, install Python 3 from python.org if needed.

Download `install.sh` as described in the [README](../../README.md), or obtain this repository and run `python3 scripts/installer.py`. Specify the Beta explicitly: `latest` resolves stable releases only.

```bash
bash install.sh install --version v0.1.7-beta.1 --agent codex
bash install.sh install --version v0.1.7-beta.1 --agent claudecode
bash install.sh install --version v0.1.7-beta.1 --agent openclaw
bash install.sh install --version v0.1.7-beta.1 --agent custom --skills-dir "$HOME/my-agent/skills"
bash install.sh install --version v0.1.7-beta.1 --agent none
```

| Content | Default location |
|---|---|
| Executable entry | `~/.local/bin/znas` |
| Versions and installation state | `~/.local/share/zettos-ainas-cli` |
| Codex skills | `~/.codex/skills/znas-*` |
| Claude Code skills | `~/.claude/skills/znas-*` |
| OpenClaw skills | `~/.agents/skills/znas-*` |

The executable and skills are symbolic links to the current version. You can link one installation to multiple agents. Updates switch all linked skills with the binary. Do not edit version directories; copy customized skills under different names.

If `znas` is not found, add `export PATH="$HOME/.local/bin:$PATH"` to `~/.bashrc` or `~/.zshrc` and reopen your terminal. The installer prints instructions without editing shell configuration. `--root` and `--bin-dir` select custom locations; use the same `--root` for later maintenance.

Existing unmanaged binaries or same-name skills stop installation. Back up or move them first. Do not delete the entire agent skills directory.

## Update and roll back

Install a published newer version to update. The installer verifies the signature, SHA-256 digest, manifest, version, and the new binary's `--version` command before switching. Previous versions remain on disk.

```bash
bash install.sh status
bash install.sh install --version <published-new-version> --agent codex
bash install.sh rollback
```

Normal errors restore previous entry points. After interruption, the next installer invocation recovers the unfinished transaction. Rollback switches both binary and linked skills. Avoid starting NAS operations during installation or rollback. Disk or OS failures may require manual recovery; journals are not backups.

## Uninstall

```bash
# Remove managed links and version files; retain NAS credentials.
bash install.sh uninstall --yes
# Also clear saved CLI accounts and their local encryption key.
bash install.sh uninstall --yes --purge-credentials
```

Cleanup removes local CLI accounts, not NAS users or data. Environment credentials and manually selected external files are outside its scope. Remove legacy keychain entries through your system password manager. Uninstall preserves executable or skill paths you replaced with other content.

## Verify downloads

Each Release lists its available platform archives, `SHA256SUMS`, and `SHA256SUMS.sig`. Use the assets attached to your chosen version. The installer pins the signing key and verifies the checksum file's signature before trusting its hashes. Verification failures stop installation. The public key is [release-signing-public.pem](../../release-signing-public.pem).

Bootstrap download relies on GitHub HTTPS. Environments requiring a reviewed installer can pin a repository commit.

```bash
openssl dgst -sha256 -verify release-signing-public.pem \
  -signature SHA256SUMS.sig SHA256SUMS
sha256sum -c SHA256SUMS
# macOS: shasum -a 256 -c SHA256SUMS
```

Manual verification of the whole list requires all listed archives. The installer downloads and verifies only your platform's archive.
