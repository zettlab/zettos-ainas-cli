# 隐私与数据流

[English](docs/en/PRIVACY.md) · **简体中文** · [文档中心](docs/README.md)

`znas` 使用你配置的 NAS 网关和账号调用 NAS 服务。账号权限由 NAS 决定。密码在终端隐藏输入；登录流程使用 NAS 提供的公钥加密密码。公网仍应使用 HTTPS，密码字段加密不能替代传输层保护。

CLI 将访问凭据保存在当前用户的本地配置目录中：Linux 默认 `~/.config/znas`，macOS 默认 `~/Library/Application Support/znas`；`XDG_CONFIG_HOME` 或 `ZETTOS_NAS_CLI_CONFIG_DIR` 可以改变位置。凭据密文和本地密钥受到文件权限保护；这不能防止已获得你系统账号权限的软件读取凭据。

安装器从 GitHub 下载安装脚本与 Release 附件，因此 GitHub 会收到正常下载请求信息。安装器和诊断脚本不主动上传 NAS 内容或诊断结果。

使用 AI Agent 时，Agent 读取的文件名、搜索摘要、问答结果或文件内容可能进入对话并发送给该 Agent 使用的模型服务。NAS 上的 AI 索引在何处处理，与 Agent 对话在何处处理是两件不同的事。请核对 Agent/模型服务的隐私设置，只开放你愿意交给它处理的内容。

安装/使用第三方 NAS 应用、外网访问和分享功能时，还应查看相应服务的隐私设置。删除 CLI 不会撤回已经发给模型服务的内容，也不会自动关闭 NAS 分享链接。

卸载默认保留登录信息；使用 `uninstall --yes --purge-credentials` 可清除当前配置目录的 CLI 账号和本地密钥。环境变量、外部凭据文件和历史系统钥匙串项目需要单独清理。
