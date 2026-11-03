# Release maintenance

**English** · [简体中文](../MAINTAINING.md) · [Documentation](README.md)

This repository contains public distribution materials only. Build private CLI code within its separate access boundary. Never copy private source/history, internal documents, accounts, or test-device configuration here.

## Release process

1. Lock versions/dependencies in the private build environment. Complete review, CLI tests, auth security checks, and real NAS acceptance.
2. Generate the nine skills with that CLI version and review their public content.
3. Build and run Linux x86_64, Linux ARM64, and macOS Apple Silicon binaries natively. Record minimum OS and firmware compatibility; assess Mac signing/notarization.
4. Generate dependency inventory, full notices, and required third-party source archives. Review advisories; unknown licensing or unhandled severe findings fail release readiness.
5. Package each built executable with `scripts/package_release.py package`, the same version, and its notices. Include only binary, skills, licenses, third-party materials, and manifest.
6. Sign the complete three-platform set with `scripts/package_release.py sign`. Keep the key outside both repositories and out of logs/assets.
7. Update both languages of acceptance, compatibility, README, and changelog. Verify packaged skills match the tag. Public validation must not require private source.
8. Run tooling tests and the public-tree scan, review the change, and use `type(scope): summary` commits with the appropriate agent Co-Authored-By trailer.
9. Create a prerelease tied to that commit as a draft, attach all three archives and signed checksums, download and verify them, then publish only after gates pass.
10. Verify unauthenticated access and clean installation, login, browsing, update/rollback, and uninstall. Record results. For a blocking regression, withdraw the recommendation and identify affected versions.

```bash
python3 scripts/package_release.py package \
  --binary /path/to/built/znas --version v0.1.7-beta.1 \
  --platform linux-x86_64 \
  --notices /path/to/notices/THIRD-PARTY-NOTICES.txt \
  --output dist/v0.1.7-beta.1
python3 scripts/package_release.py sign \
  --directory dist/v0.1.7-beta.1 --private-key /protected/path/signing.pem
```

The notices directory must include `dependency-inventory.json`, required `third-party-sources/` files, and `rust-runtime-notices/`. Missing materials, incorrect architecture, or a mismatched signing key must fail packaging/signing. Do not silently replace version assets; fixes require a new version.

## Signing and CI

The public key is stored in `release-signing-public.pem` and embedded in the installer. Back up the private key separately with restricted access. Rotation is an explicit release event: review the new key, update the installer, and explain trust migration. Maintainers should use two-factor authentication and minimal publishing permissions.

Public CI tests tooling on three native platforms, without private source, signing keys, or NAS credentials. Green tooling tests are not evidence of real CLI or NAS acceptance.

After uploading draft assets, manually run `Verify signed release binaries` with the tag. It verifies signature, installation, version, schemas, destructive-command rejection, and uninstall, saving asset-digest evidence.

GitHub [draft visibility](https://docs.github.com/en/rest/releases/releases#list-releases) requires push access. Only the independent download job receives `contents: write`; it neither checks out code nor executes assets. Short-lived artifacts pass the bytes to read-only execution jobs with checkout credential persistence disabled. No step publishes or edits a Release.

During development, `sign --candidate` may sign an incomplete platform set for draft checks. `linux_only` verifies the two Linux candidates; it does not pass full release acceptance. Before publication, add every platform, regenerate the complete signed list, and run all-platform verification.
