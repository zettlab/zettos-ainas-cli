# Zettlab AINAS CLI

**English** · [简体中文](README.zh-CN.md)

Connect your terminal or AI agent to your Zettlab NAS. Browse files, search your content, retrieve context for questions, and manage NAS services with the permissions of your NAS account.

**Pre-release: the first public Beta is not available for download yet.** Signed Linux candidates passed native installer checks. NAS workflow acceptance and the Apple Silicon build remain incomplete. The commands below become usable when the corresponding Release is published. See the [acceptance record](docs/en/ACCEPTANCE.md).

[Documentation](docs/en/README.md) · [Compatibility](docs/en/COMPATIBILITY.md) · [Support](SUPPORT.md) · [Releases](https://github.com/zettlab/zettos-ainas-cli/releases)

## What you can do

| Goal | Entry point |
|---|---|
| Browse your NAS files | `znas file root spaces` |
| Find files and photos | `znas search --query 'cats'` |
| Retrieve context for a question | `znas ask --question 'Summarize the product launch plan'` |
| Check your device | `znas settings device info` |
| Use an AI agent | Nine supplied skills for Codex, Claude Code, OpenClaw, or a custom directory |

Additional commands cover applications, containers, photos, Coder, Theater, and desktop status. Availability depends on firmware, installed services, and account permissions. Validation levels differ by module; see the [support matrix](docs/en/COMPATIBILITY.md).

`znas ask` retrieves NAS context; the agent or model produces the conversational answer. File names, excerpts, and content read by an agent may reach its model provider. Read the [privacy guide](docs/en/PRIVACY.md) before connecting private data.

## Get started

Complete NAS initialization, account setup, and storage setup in the official Zettlab interface first. Install the CLI on the computer running your agent. NAS SSH access is not required. You need Python 3.9+, curl, and OpenSSL; you do not need Rust or a GitHub account.

After the Beta is published, download and review the installer:

```bash
curl --proto '=https' --proto-redir '=https' -fsSL \
  https://raw.githubusercontent.com/zettlab/zettos-ainas-cli/main/install.sh -o install.sh
bash install.sh install --version v0.1.7-beta.1 --agent codex
export PATH="$HOME/.local/bin:$PATH"
znas --version
```

Replace `codex` with `claudecode` or `openclaw`, or use `none` for CLI-only installation. Installation uses your user account without sudo. See [installation and version management](docs/en/INSTALL.md) for custom directories, updates, rollback, and uninstall.

Connect using the gateway address you use to access the NAS:

```bash
znas --base-url 'http://<NAS-address>:<port>' auth probe
znas --base-url 'http://<NAS-address>:<port>' auth login --username '<NAS-username>' --keep-logged-in
# Enter your password at the hidden terminal prompt.
znas file root spaces
znas file root list --json '{"path":"/personal","size":20,"index":0}'
znas search --query 'cats'
```

Do not put passwords in chat or command arguments. Use a reachable HTTPS gateway for remote connections. The [first connection guide](docs/en/QUICKSTART.md) covers account aliases, file browsing, and AI prerequisites.

Restart or refresh your agent's skills, then try:

> List the files in my NAS personal space.
>
> Find photos of cats on my NAS.
>
> Summarize the product launch documents on my NAS.

## Project and support

The Rust implementation remains private. This repository contains public distribution tooling, documentation, and nine agent skills. Binaries will be distributed through signed GitHub Release archives.

- [Troubleshooting](docs/en/TROUBLESHOOTING.md) and [support channels](SUPPORT.md)
- [Privacy](docs/en/PRIVACY.md) and [private security reports](docs/en/SECURITY.md)
- [Changelog](docs/en/CHANGELOG.md), [release readiness](docs/en/READINESS.md), and [language coverage](docs/en/LOCALIZATION.md)
- [Contributing to public tooling and documentation](CONTRIBUTING.md)

Documentation is available in English and Simplified Chinese. Installer and CLI messages are currently English; translated documentation does not change runtime language. This Beta has no response-time SLA or long-term support commitment.

The binary is governed by [LICENSE](LICENSE). Public scripts, documentation, and skills use [TOOLING-LICENSE](TOOLING-LICENSE). Third-party components retain their own licenses and notices, supplied in each platform archive.
