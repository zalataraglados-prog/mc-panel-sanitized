Highlights / 亮点
Wizard UI defaults and catalog experience improved: UTF-8 fixes, advanced parameters now in a modal, and profile filtering aligned with taxonomy keys.
导引页面默认值与目录体验优化：修复 UTF-8 乱码，高级参数改为弹窗，并对齐 taxonomy 的档位过滤逻辑。
Deployment now actually executes actions; wizard waiting/health logic hardened to avoid false success or endless waits.
部署器开始真实执行 Actions；导引等待与健康检查逻辑加固，避免假成功或无限等待。
CLI and installer reliability improved: CLI entry restored, mcic wrapper installed, wizard-first default with CLI fallback.
CLI/安装可靠性提升：修复 CLI 入口，安装 mcic wrapper，默认走导引网页，CLI 作为备用路线。
Packaging cleanup: removed legacy setup.py from deploy to avoid confusion.
打包清理：移除 deploy 目录下的旧 setup.py，避免混淆。
Documentation cleanup: removed outdated release drafts/announcement and a one-off deploy report.
文档清理：移除过期的发布草稿/公告和一次性的部署报告。
BlueMap download link hotfix: replaced stale `latest/download/bluemap-5.15-spigot.jar` with the valid v5.16 asset URL.
BlueMap 下载链接热修复：将失效的 `latest/download/bluemap-5.15-spigot.jar` 替换为有效的 v5.16 资源地址。
Apply failure handling improved: wizard now reports concrete CLI failure lines and performs service/compose teardown for failed instances.
Apply 失败处理增强：向导会显示更具体的 CLI 失败行，并对失败实例执行 service/compose 下线。
Execution order adjusted: plugin/map downloads are executed before MC service startup to avoid partial-live state on download failures.
执行顺序调整：插件/地图下载前置到 MC 服务启动之前，避免下载失败时进入半成功运行态。

Technical Notes / 技术说明
This release focuses on stability of the wizard + deployment pipeline and reduces operator confusion.
本次更新聚焦导引与部署链路的稳定性，并降低运维误判风险。

Notes / 备注
If you encounter errors, copy the error output + this release note for faster diagnosis.
如遇报错，请将报错与本说明一并复制，便于快速定位。

Acknowledgements / 致谢
Thanks to all testers for validating the wizard/apply flow.
感谢所有测试人员对导引与部署流程的验证与反馈。
