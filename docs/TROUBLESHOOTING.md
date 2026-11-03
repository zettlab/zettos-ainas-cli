# 常见问题

[English](en/TROUBLESHOOTING.md) · **简体中文** · [文档中心](README.md)

| 现象 | 处理 |
|---|---|
| `znas: command not found` | 检查 `~/.local/bin` 是否在 PATH；重新打开终端 |
| 最新版本无法解析 | Beta 使用 `--version v0.1.7-beta.1`；确认 Release 已发布 |
| 签名或校验失败 | 停止安装；重新下载官方附件；不要禁用验证 |
| 已有文件/链接冲突 | 备份原有 `znas` 或同名 skills；安装器不会强制覆盖 |
| 无法连接 / 超时 | 用浏览器核对同一 NAS 地址、端口和网络，再运行 `auth probe` |
| 证书错误 | 使用匹配证书的主机名和可信证书，不跳过校验 |
| 登录过期 | 使用 `auth refresh`；没有有效 refresh token 时重新登录 |
| 权限不足 | 检查 NAS 用户实际拥有的权限，不自动升级为管理员 |
| 找不到 AI 搜索结果 | 先验证文件浏览和关键字搜索，再检查 NAS 模型与索引状态 |
| Agent 找不到 skills | 核对安装时的 Agent 类型和目录，刷新或重启 Agent |

反馈时提供：CLI 版本、电脑系统/CPU、NAS 固件版本、操作步骤、错误摘要，以及是否通过 `auth probe`。请先自行检查文本，删去密码、token、用户名、设备序列号、完整私人文件路径和分享链接。

本地诊断可运行：

```bash
python3 scripts/diagnose.py --binary znas
```

该脚本只输出操作系统/架构、Python/OpenSSL 与 CLI 版本信息；不读取 NAS 内容、不联网、不读取凭据、不自动上传。NAS 连通性由你单独运行 `znas --base-url '<地址>' auth probe` 检查，公开反馈前删除地址。

程序错误请发普通 Issue；涉及越权、凭据暴露或数据泄露的问题请走 [SECURITY.md](../SECURITY.md)，不要上传公开日志。
