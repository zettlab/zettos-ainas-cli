# Zettlab AINAS CLI

[English](README.md) · **简体中文** · [文档中心](docs/README.md)

用命令行或 AI Agent 操作你的 Zettlab NAS：浏览文件、搜索内容、查询设备状态，以及管理应用、容器和照片。

**当前状态：首个公开 Beta 正在准备，尚未发布可下载版本。** 安装器与文档已提供；下面的安装命令在对应 Release 发布后可用。支持平台和使用条件见[兼容性说明](docs/COMPATIBILITY.md)。

本仓库提供安装工具、用户文档和 9 个 Agent skills。`znas` 的 Rust 实现保持私有，编译后的程序通过 [GitHub Releases](https://github.com/zettlab/zettos-ainas-cli/releases) 分发。使用时不需要 Rust、源码或 GitHub 账号。

## 可以做什么

| 目标 | 入口 |
|---|---|
| 浏览 NAS 文件 | `znas file root spaces` |
| 查找文件与照片 | `znas search --query '猫'` |
| 为内容问题检索上下文 | `znas ask --question '总结产品发布计划'` |
| 查询设备信息 | `znas settings device info` |
| 接入 AI Agent | 为 Codex、Claude Code、OpenClaw 或自定义目录安装九个 skills |

功能可用性取决于 NAS 固件、服务和账号权限；各功能使用条件不同，请先查看[兼容性](docs/COMPATIBILITY.md)。

## 开始使用

请先在 Zettlab 官方界面完成 NAS 初始化，确认电脑能打开 NAS 登录页面。安装在你运行 Agent 的电脑上；NAS 不需要开启 SSH。

[文档中心](docs/README.md) · [支持与反馈](SUPPORT.zh-CN.md)

准备 Python 3.9+、curl 和 OpenSSL，在 Beta 发布后下载并查看安装脚本：

```bash
curl --proto '=https' --proto-redir '=https' -fsSL \
  https://raw.githubusercontent.com/zettlab/zettos-ainas-cli/main/install.sh -o install.sh
bash install.sh install --version v0.1.7-beta.1 --agent codex
```

可将 `codex` 换为 `claudecode`、`openclaw`；只使用命令行则用 `none`。默认不使用 sudo，程序入口放在 `~/.local/bin/znas`。

```bash
export PATH="$HOME/.local/bin:$PATH"
znas --version
znas --base-url 'http://<NAS地址>:<端口>' auth probe
znas --base-url 'http://<NAS地址>:<端口>' auth login --username '<NAS用户名>' --keep-logged-in
# 在终端隐藏输入密码，不要把密码发给 Agent。
znas file root spaces
znas file root list --json '{"path":"/personal","size":20,"index":0}'
znas search --query '猫'
```

地址填写你实际可以访问的 NAS 网关地址。远程连接、证书与密码说明见 [快速开始](docs/QUICKSTART.md)。

完成登录后，重新启动或刷新 Agent 的 skills，然后试着说：

> 列出我 NAS 个人空间里的文件。
>
> 帮我找 NAS 里拍到猫的照片。
>
> 总结 NAS 里关于产品发布计划的内容。

## 使用与支持

- [安装、升级、回退、卸载](docs/INSTALL.md)
- [系统与 NAS 兼容性](docs/COMPATIBILITY.md)
- [常见问题与诊断](docs/TROUBLESHOOTING.md)
- [隐私与 AI 数据流](PRIVACY.md)
- [安全反馈](SECURITY.md)
- [更新记录](CHANGELOG.md)
- [普通问题反馈](https://github.com/zettlab/zettos-ainas-cli/issues/new/choose)

使用范围包括 `file`、`settings`、`app-store`、`docker`、`photos`、`coder`、`theater` 和桌面状态；各模块使用条件见兼容性表。搜索使用 `znas search`，内容问答使用 `znas ask`。权限来自登录的 NAS 账号。

程序许可见 [LICENSE](LICENSE)。公开安装工具、文档和 skills 使用 [TOOLING-LICENSE](TOOLING-LICENSE)。第三方组件声明随每个平台安装包交付。

`znas ask` 提供 NAS 检索上下文，最终对话回答由 Agent/模型生成；文件名、摘要和文件内容可能进入模型服务，使用前请阅读隐私说明。

文档提供中英文版本；安装器与 CLI 提示目前仍为英文。文档翻译不代表运行时已支持切换语言，见[多语言覆盖](docs/LOCALIZATION.md)。当前 Beta 没有响应时间 SLA 或长期支持承诺。问题和文档建议请通过[支持渠道](SUPPORT.zh-CN.md)反馈。
