# 发行维护

本仓库只维护公开交付内容。私有 CLI 代码在独立权限边界内构建；不得把源码、内部文档、账号、测试设备配置或私有 Git 历史复制进来。

## 发布步骤

1. 私有构建环境锁定版本与依赖，完成代码审查、CLI 测试、认证安全验收和真实 NAS 验收。
2. 用该版本的 CLI 生成九个 skills 到本仓库，审核公开内容。
3. 构建并在对应目标平台运行 Linux x86_64、Linux ARM64、macOS Apple Silicon 程序。记录最低系统版本与 NAS 固件兼容性；macOS 完成代码签名/公证评估。
4. 生成依赖清单、完整许可证文本和需要随附的第三方源码包。审核漏洞清单；不可将许可未知或有未处理严重漏洞的附件当作合格发行包。
5. 每个平台执行 `scripts/package_release.py package`，输入已构建的程序、相同版本号和依赖声明。包只包含程序、skills、许可证、第三方材料和 manifest。
6. 全部三平台包就绪后执行 `scripts/package_release.py sign`。签名私钥通过 `--private-key` 指向仓库外受保护位置；不要把密钥文件或其内容放进 Git、日志或附件。
7. 完成 `ACCEPTANCE.md` 证据表，更新兼容性文档、README 和更新日志；测试不能访问 CLI 源码。确认程序包和 Git 标签的 skills 完全一致。
8. 运行公开工具测试与 `scripts/check_public_tree.py`，审查提交。使用 `type(scope): summary`，Agent 生成的提交保留对应 Co-Authored-By trailer。
9. 创建与该提交绑定的 GitHub 预发布版，先上传为 draft：三个平台包、SHA256SUMS、SHA256SUMS.sig。下载 draft 附件复验后发布。
10. 使用无登录状态的客户端检查 README、安装脚本和 Release 附件，再在干净环境完成安装、登录、文件浏览、升级/回退和卸载。记录结果；如发布后发现阻断性问题，撤回推荐并说明受影响版本。

打包示例（在本仓库执行）：

```bash
python3 scripts/package_release.py package \
  --binary /path/to/built/znas --version v0.1.7-beta.1 \
  --platform linux-x86_64 \
  --notices /path/to/notices/THIRD-PARTY-NOTICES.txt \
  --output dist/v0.1.7-beta.1
python3 scripts/package_release.py sign \
  --directory dist/v0.1.7-beta.1 --private-key /protected/path/signing.pem
```

notices 同目录必须有 `dependency-inventory.json`、其要求的 `third-party-sources/` 文件以及 Rust 标准库的 `rust-runtime-notices/` 许可材料。来源不完整、架构错误或签名公钥不匹配时打包/签名应失败。版本附件不得静默覆盖；修复需要新版本号。

## 密钥与维护权限

当前公钥存于 `release-signing-public.pem`，并内嵌在安装器中。私钥需要维护方单独备份与权限管理。密钥轮换要作为明确发布事件：审查新公钥、同步安装器、说明旧版本用户如何更新信任。GitHub 组织应启用双因素认证，并只给发布任务最小权限。

## CI 的范围

公开 CI 在 Linux x86_64、Linux ARM64 与 macOS 上测试安装工具，不接触私有源码、签名私钥或真实 NAS 凭据。公开 CI 的绿灯只证明安装工具测试通过；不等于三平台 CLI 已验证或 NAS 验收已完成。

三平台附件上传到 draft Release 后，手动运行 `Verify signed release binaries`，填写该版本标签。它会在对应原生 runner 上验证签名、安装、程序版本、schema、高风险命令拒绝和卸载，并保存带附件摘要的 JSON 证据。只有实际执行成功的结果才能填写为原生二进制验收通过。

开发期间可以用 `sign --candidate` 为不完整的平台集合签名并上传 draft，选 `linux_only` 先验证 Linux 两个平台。该结果只代表 Linux 候选包，不能替代三平台发布验收；正式发布前必须补齐全部附件、重新生成完整签名清单，并运行不带 `linux_only` 的验收。
