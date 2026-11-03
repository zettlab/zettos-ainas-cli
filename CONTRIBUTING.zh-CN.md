# 贡献指南

[English](CONTRIBUTING.md) · **简体中文** · [文档中心](docs/README.md)

欢迎改进安装工具、文档、翻译、反馈表单与公开 skills。Rust 实现保持私有，本仓库不接收或公开私有实现文件和历史。CLI 行为问题请通过[支持渠道](SUPPORT.zh-CN.md)反馈。

1. 描述问题和预期用户行为；较大改动先在 Issue 中讨论。
2. 每次修改聚焦一个目标，保留安装恢复机制、凭据保护和用户原有文件。
3. 行为、命令、警告、兼容性或隐私事实变化时，在同一批修改中同步中英文，遵循[多语言规范](docs/LOCALIZATION.md)。
4. 审查差异中的凭据、设备信息、内部链接和私有源码，不添加真实 NAS 数据或签名私钥。
5. 在 PR 中说明变化和验证，区分已经验证的证据与未测试的平台声明。

工具改动在仓库根目录执行：

```bash
python3 -m unittest discover -s tests -v
bash -n install.sh
python3 scripts/installer.py --help
python3 scripts/check_public_tree.py
```

公开内容扫描器检查 Git 已跟踪文件，因此新增文件需先加入暂存区。纯文档改动检查相对链接、示例、语言对应关系和发布状态一致性；未改变示例或行为时不需要重跑二进制/NAS 测试。不要为了验证文档对真实 NAS 执行破坏性命令。

提交信息采用 `type(scope): summary`，Agent 生成的提交附对应 Co-Authored-By。公开贡献遵循 [TOOLING-LICENSE](TOOLING-LICENSE)，独立的[二进制许可](LICENSE)不受影响。漏洞按[安全指南](SECURITY.md)私密报告。
