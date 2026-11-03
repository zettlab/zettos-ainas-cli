# 平台与功能要求

[English](en/COMPATIBILITY.md) · **简体中文** · [文档中心](README.md)

**当前尚未发布可下载版本。** 可用的平台包、最低系统版本与支持的 NAS 固件，以对应 Release 说明为准。

| 电脑平台 | 下载计划 |
|---|---|
| Linux x86_64 | 计划提供 `znas-linux-x86_64.tar.gz` |
| Linux ARM64 | 计划提供 `znas-linux-aarch64.tar.gz` |
| macOS Apple Silicon | 计划提供 `znas-macos-aarch64.tar.gz` |
| Windows / Intel Mac | 暂不提供；不承诺 WSL 或 Rosetta 兼容性 |

安装需要 Python 3.9+、curl 和 OpenSSL。CLI 安装在运行终端或 Agent 的电脑上，通过 NAS 网关连接，不需要开启 NAS SSH。

| 功能 | 使用条件 |
|---|---|
| 登录、文件浏览 | 可访问的网关、已有 NAS 账号、已完成存储设置、相应文件权限 |
| 搜索、内容问答 | 文件权限；AI 功能还需要相应 NAS 服务、模型和内容索引 |
| 设备设置与桌面状态 | 相应 NAS 服务；部分操作需要管理员权限 |
| 应用与容器 | 相应服务和可用存储空间 |
| 照片 | 照片应用与索引 |
| Coder、Theater | 已安装对应应用，并可通过网关访问 |
| 外网连接 | 已完成官方远程访问设置，可访问的 HTTPS 网关 URL |

不同 NAS 固件和应用版本可能提供不同功能。`auth probe` 成功只表示认证入口可达，不代表所有功能可用。出现 `404`、服务不可达或权限不足时，先核对固件、应用版本与账号权限；见[常见问题](TROUBLESHOOTING.md)。

CLI 不会使用主机原生命令替代 NAS 控制 API。Linux 系统不满足程序的 glibc 要求时，安装预检会失败并保留原版；不要为了安装 CLI 替换系统 glibc。
