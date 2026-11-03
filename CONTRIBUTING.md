# Contributing

**English** · [简体中文](CONTRIBUTING.zh-CN.md) · [Documentation](docs/en/README.md)

Contributions are welcome for this repository's installation tooling, documentation, translations, issue forms, and public skills. The Rust implementation is private; this repository does not accept or expose private implementation files or history. Report CLI behavior problems through [support](SUPPORT.md).

1. Describe the problem and expected user behavior. Discuss substantial changes in an issue before implementation.
2. Keep the change focused and preserve managed-installation recovery, credential protection, and existing user files.
3. Update both English and Chinese guides in the same change when behavior, commands, warnings, compatibility, or privacy facts change. Follow [localization](docs/en/LOCALIZATION.md).
4. Review the diff for credentials, device data, internal links, and private source. Do not include real NAS fixtures or signing keys.
5. Explain the change and validation in the pull request. Separate verified evidence from untested platform claims.

For tooling changes, run from the repository root:

```bash
python3 -m unittest discover -s tests -v
bash -n install.sh
python3 scripts/installer.py --help
python3 scripts/check_public_tree.py
```

The tree scanner checks Git-tracked files, so stage intended new files before running it. For documentation-only edits, check relative links, examples, language pairs, and release-status consistency; binary or NAS tests are not needed unless examples or behavior changed. Do not run destructive commands on a real NAS to validate docs.

Use `type(scope): summary` commit messages. Agent-generated commits must include the appropriate Co-Authored-By trailer. Public contributions are governed by [TOOLING-LICENSE](TOOLING-LICENSE); the separate [binary license](LICENSE) is unchanged. Report vulnerabilities privately using the [security guide](docs/en/SECURITY.md).
