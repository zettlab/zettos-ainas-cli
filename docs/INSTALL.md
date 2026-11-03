# 安装与版本管理

[English](en/INSTALL.md) · **简体中文** · [文档中心](README.md)

计划交付 Linux x86_64、Linux ARM64 和 macOS Apple Silicon。当前 Linux 两种架构的候选程序已在 Ubuntu 24.04 原生验证，macOS 程序尚待构建和验收，公开 Release 尚未发布。请以[兼容性记录](COMPATIBILITY.md)和[验收记录](ACCEPTANCE.md)为准；以下安装命令需在对应版本正式开放下载后使用。

Python 3.9+、curl、OpenSSL 必须在 PATH 中；不需要安装 Rust。Windows 原生和 Intel Mac 暂不支持。macOS 若没有 Python，请先从 python.org 安装 Python 3。

从 README 下载 `install.sh`，或下载本仓库后直接使用 `python3 scripts/installer.py`。首次 Beta 必须指定版本；`latest` 仅解析正式版本，不会自动安装预发布版。

```bash
bash install.sh install --version v0.1.7-beta.1 --agent codex
bash install.sh install --version v0.1.7-beta.1 --agent claudecode
bash install.sh install --version v0.1.7-beta.1 --agent openclaw
bash install.sh install --version v0.1.7-beta.1 --agent custom --skills-dir "$HOME/my-agent/skills"
bash install.sh install --version v0.1.7-beta.1 --agent none
```

默认安装目录：

| 内容 | 位置 |
|---|---|
| 程序入口 | `~/.local/bin/znas` |
| 完整版本与安装状态 | `~/.local/share/zettos-ainas-cli` |
| Codex skills | `~/.codex/skills/znas-*` |
| Claude Code skills | `~/.claude/skills/znas-*` |
| OpenClaw skills | `~/.agents/skills/znas-*` |

skills 和程序入口是符号链接，整体指向当前版本。可以给多个 Agent 安装同一版本。升级时所有已链接的 skills 一同切换。请勿直接修改版本目录；自定义 skills 应复制到不同名称的目录。

如果提示找不到 `znas`，把 `export PATH="$HOME/.local/bin:$PATH"` 加入 `~/.bashrc` 或 `~/.zshrc` 后重新打开终端。安装器只提示，不擅自编辑你的配置。使用 `--root`、`--bin-dir` 可指定安装位置；后续维护必须使用同一个 `--root`。

如果已有手工安装的 `znas` 或同名 skills，安装器会停止。请先备份或移走它们，再安装；不要删除整个 Agent 的 skills 目录。

## 更新与回退

再次安装指定的新版本即可更新。程序会先验证签名、SHA-256、文件清单和版本，并运行新程序的 `--version`。全部通过后才切换入口。历史版本保留在本机。

```bash
bash install.sh status
bash install.sh install --version <已发布的新版本> --agent codex
bash install.sh rollback
```

普通错误会恢复原入口；进程异常退出后，下次启动安装器会恢复未完成的事务。回退会同时切换二进制和全部已安装的 skills。不要在安装或回退过程中运行新的 NAS 操作。磁盘或操作系统故障可能需要人工恢复；事务日志不替代系统备份。

## 卸载

```bash
# 删除本工具管理的程序入口、skills 链接和版本文件，保留 NAS 登录信息。
bash install.sh uninstall --yes

# 同时清除本地 znas 账号和本地加密密钥。
bash install.sh uninstall --yes --purge-credentials
```

清除凭据只影响 znas 本地账号，不删除 NAS 用户、不删除 NAS 数据。环境变量和手工指定的外部凭据文件不在清理范围内；历史版本遗留的系统钥匙串项可在系统密码管理器中删除。卸载不会删除被你替换成其他内容的程序入口或 skills。

## 下载验证

完整发行版将包含三个平台包、`SHA256SUMS` 和 `SHA256SUMS.sig`；当前草稿仅有两个 Linux 候选包。安装器内置发布公钥；必须通过签名验证才能使用校验和，验证失败不会安装。公开公钥在 `release-signing-public.pem`。下载 Bootstrap 安装脚本依赖 GitHub HTTPS；高要求环境可以固定已审阅的仓库提交再运行安装器。

手工验证示例：

```bash
openssl dgst -sha256 -verify release-signing-public.pem \
  -signature SHA256SUMS.sig SHA256SUMS
sha256sum -c SHA256SUMS  # macOS 可用 shasum -a 256 -c SHA256SUMS
```

校验时应下载清单所列的全部附件；安装器只下载并核验当前平台附件。
