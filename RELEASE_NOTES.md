# MC Panel v1.0.0 Release Notes / v1.0.0 发布说明

This release marks the first stable, publishable version of the Minecraft Configuration Decision Engine with optional runtime panel.
这是 Minecraft 配置裁决引擎的首个可发布稳定版本，包含可选运行期面板。

Highlights / 亮点
- Rules-driven planning: catalog + taxonomy + planner -> allow/warn/block/recommend.
- Loader: pulls rules from remote repository, injects into planner.
- Execution Plan (dry-run): deterministic, auditable plan output.
- Claims string: import/export of params-only payloads.
- Optional runtime panel: FastAPI backend + React frontend.

- 规则驱动规划：catalog + taxonomy + planner -> allow/warn/block/recommend。
- Loader：从远端规则仓库拉取并注入 planner。
- 执行计划（dry-run）：确定性、可审计。
- Claims 字符串：仅 params 的导入/导出。
- 可选运行期面板：FastAPI 后端 + React 前端。

Key Features / 核心功能
- Review output: warnings, blocks, recommendations.
- CLI: plan/apply (dry-run default), instances listing, panel install/uninstall.
- Panel: metrics, logs, command/RCON, player list, map tiles, rules editor, inventory (via optional plugin).
- Map plugins: Dynmap/BlueMap optional support, config reload via RCON.
- Plugin download logging with optional git push to logs branch.

- Review 输出：warnings / blocks / recommendations。
- CLI：plan/apply（默认 dry-run）、实例列表、面板安装/卸载。
- 面板：指标、日志、命令/RCON、玩家列表、地图瓦片、规则编辑、背包（可选插件）。
- 地图插件：Dynmap/BlueMap 可选支持，RCON 重载配置。
- 插件下载日志：可选推送到仓库 logs 分支。

Notes / 说明
- Panel is optional and can be installed later.
- This release does not auto-apply recommendations or execute system changes by default.

- 面板为可选项，可部署后补装。
- 本版本不会自动应用推荐或执行系统更改。

Changes since demon1.1 baseline / 相对 demon1.1 基线的变化
- API aggregation and throttling (summary endpoint, cache).
- Frontend polling throttled to reduce load.
- Optional CLI event logging.
- Documentation updates for summary API and CLI logs.

- API 聚合与节流（summary 端点、缓存）。
- 前端轮询节流降低负载。
- 可选 CLI 事件日志。
- 文档更新（summary API 与 CLI 日志）。
