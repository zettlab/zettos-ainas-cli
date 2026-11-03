# 第一次连接 NAS

[English](en/QUICKSTART.md) · **简体中文** · [文档中心](README.md)

1. 先通过 Zettlab 官方界面完成 NAS 初始化、账号和存储设置。官方入口：[Zettlab Wiki](https://wiki.zettlab.com/)。
2. 在运行 Agent 的电脑浏览器中打开 NAS 页面，记下实际使用的地址和端口。初次连接优先使用同一局域网。
3. 安装程序后先检测连接，再登录：

```bash
znas --base-url 'http://<NAS地址>:<端口>' auth probe
znas --base-url 'http://<NAS地址>:<端口>' auth login --username '<用户名>' --keep-logged-in
znas auth status
```

登录会隐藏密码输入。不要把 NAS 密码粘贴进聊天，也不要把真实密码写在命令参数里。自动化场景可让密码管理器通过管道传给 `auth login --password-stdin`，每次输入一行；不要在脚本中硬编码密码。

`auth probe` 只证明认证入口可达，不能证明所有模块可用。CLI 保存的账号用于后续命令；多个 NAS 可通过登录时的 `--account <别名>` 区分，然后在命令前使用全局 `--account <别名>`。

先验证你自己的个人空间：

```bash
znas file root spaces
znas file root list --json '{"path":"/personal","size":20,"index":0}'
```

列出的子目录可能返回实际存储路径，继续浏览时复制返回的完整路径。不要猜存储池路径，也不要用 `/` 作为首次浏览入口。

查找与问答分别使用：

```bash
znas search --query '猫'
znas ask --question '总结 NAS 里关于产品发布计划的内容'
```

AI 搜索和问答依赖 NAS 相应服务、模型及内容索引；未准备好时先确认普通文件浏览是否正常。`znas ask` 返回检索上下文，由 Agent/模型生成最终回答。Agent 可能把返回内容发送给其模型提供商，参见[隐私说明](../PRIVACY.md)。

外网访问请先按官方设置完成并验证可访问的 HTTPS 网关地址。CLI 需要实际网关 URL，不接受协助码或设备编号代替 URL。不要把局域网 HTTP 服务直接暴露到公网；不要通过跳过证书验证解决 TLS 错误。当前远程接入模式仍需逐项实机验证，见兼容性记录。

浏览、搜索先用普通 NAS 用户。只有需要管理设备、用户或共享权限时才使用具备相应权限的账号。删除、覆盖、分享、安装应用和修改设置前，确认操作对象与影响范围。

当前测试固件签发的刷新令牌仅有效 1 秒，立即刷新成功但稍后刷新被拒绝，长期保持登录尚未验收。详见[验收记录](ACCEPTANCE.md)；刷新被拒绝时请通过隐藏密码提示重新登录。
