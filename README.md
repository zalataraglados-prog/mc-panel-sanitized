---

## CHANGELOG.md

﻿# Changelog / 更新日志

## [Unreleased] / 未发布

## [2026-01-24]
### Added / 新增
- Full Chinese item name map in inventory UI using the official `zh_cn.json`.
  - 背包界面接入官方 `zh_cn.json`，物品中文名全量覆盖。
- Owner panel with per-instance `owners.json`, owner-only controls, and logout button.
  - 新增服主栏（实例级 `owners.json`）、服主专属操作与退出登录按钮。

### Changed / 调整
- Map view simplified to embed the external BlueMap page (port 8100) with a dedicated open button.
  - 地图改为内嵌 8100 端口 BlueMap 预览，并提供“打开详细地图”按钮。
- Inventory editing UI switched to a slot grid with hotbar at the bottom.
  - 背包编辑界面改为格子布局，快捷栏在底部。

### Fixed / 修复
- Inventory read/write supports offline playerdata and online editing via RCON item replace.
  - 支持离线 NBT 读取与在线 RCON 写入背包。
- Memory format normalization for decimal values to avoid JVM `-Xmx` errors.
  - 内存小数格式自动标准化，避免 JVM 启动失败。

## [2026-01-06]
### Added / 新增
- RCON health check endpoint and UI status badge (`/api/rcon/health`, status tag in dashboard).
  - 新增 RCON 健康检查接口与面板状态标识（`/api/rcon/health`）。
- Claims export API (`/api/claims/export`) and UI button to export the full defaults + overrides as a claims string.
  - 新增配置导出接口与面板导出按钮（全量默认 + 覆盖）。
- Gamerule export via RCON during claims export (fallback to defaults when RCON fails).
  - 导出时通过 RCON 读取 gamerule（失败则回退默认值）。
- Recommendation sampling tool for planner validation (`deploy/tools/recommendation_sampling.py`).
  - 新增 Planner 推荐采样验证脚本。
- Player OP level selector (1-4) in the player card UI.
  - 玩家卡片新增 OP 等级选择（1-4）。

### Changed / 调整
- RCON connection now resolves host port from instance `config.json` or `docker-compose.yml` before falling back to `server.properties`.
  - RCON 连接优先从 `config.json` / `docker-compose.yml` 读取端口，失败才回退 `server.properties`。
- Planner scope warnings now trigger only when a parameter is explicitly changed (avoids default-noise warnings).
  - 仅当参数被显式修改时才触发 scope 警告，避免默认值噪音。
- Capacity guard: warn when `memory <= required` (keeps block thresholds intact).
  - 容量护栏：`memory <= required` 时警告（block 门槛不变）。
- install.sh now pre-fills params with catalog defaults and merges imported claims; prompt loop uses defaults as visible values.
  - install.sh 预填 catalog 默认值并合并导入配置；交互显示默认值。

### Fixed / 修复
- Claims import no longer loses defaults when used in combination with manual overrides.
  - 导入字符串与手动覆盖组合时不会丢失默认值。
- Web UI now exposes clear RCON error feedback.
  - 面板显示更清晰的 RCON 错误反馈。


---

## PATCH_ANNOUNCEMENT_v1.0.2.md

﻿Patch Announcement / 补丁公告 (v1.0.2)

This is a patch announcement for v1.0.2. It does not change the release tag.
这是 v1.0.2 的补丁公告，不更改发布标签。

Highlights / 亮点
- Inventory now shows armor/offhand slots and keeps the hotbar at the bottom.
  背包显示盔甲/副手槽位，快捷栏固定在最底行。
- Added permanent ban action and a dedicated banned-players list.
  新增永久封禁按钮与封禁玩家栏（移出即解封）。

Notes / 备注
- Frontend needs rebuild after pulling updates.
  更新后需重新构建前端。


---

## README.md

﻿# MC Panel 

## Release Notice / 发布声明

- Important: The first two releases (v1.0.0 / v1.0.1) contain critical defects and must not be used in production.
- 重要：前两个正式版（v1.0.0 / v1.0.1）存在严重缺陷，请勿用于生产环境。
- If you hit an error, copy the error output together with this README and share it with any AI you can reach; it resolves most issues quickly.
- 如遇报错，将报错连同本介绍复制给你能接触到的 AI，可以解决绝大部分问题。

## Release / 当前发布

- Current release: `v1.0.2`
- Tag: `https://github.com/zalataraglados-prog/mc-panel-sanitized/releases/tag/v1.0.2`
- Notes: see `RELEASE_DRAFT_v1.0.2.md`

- 当前版本：`v1.0.2`
- 标签：`https://github.com/zalataraglados-prog/mc-panel-sanitized/releases/tag/v1.0.2`
- 说明：见 `RELEASE_DRAFT_v1.0.2.md`

This project is a configuration decision engine for Minecraft deployments with an optional runtime panel.
本项目是一个 Minecraft 部署前的配置裁决引擎，运行期面板为可选组件。

## Quick start (plan + dry-run) / 快速开始

```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/v1.0.2/install.sh | sudo bash
```
### Docker mirror & proxy pull / Docker 镜像加速与代理拉取

If Docker Hub is unreachable, the installer auto-applies a CN mirror fallback based on region hints (timezone/IP). It no longer prompts.
当 Docker Hub 不可达时，安装脚本会根据地区提示（时区/IP）自动应用国内镜像，不再提示。

Environment variables (override behavior):
环境变量（手动覆盖）：

- `MC_PANEL_DOCKER_MIRRORS` (comma-separated, e.g. `https://a.mirror,https://b.mirror`)
- `MC_PANEL_DOCKER_MIRROR` (legacy single mirror, still supported)
- `MC_PANEL_DOCKER_PROXY_PREFIX` (e.g. `m.daocloud.io/docker.io`)

If `itzg/minecraft-server:latest` already exists locally, the installer skips proxy pre-pull.
若本地已存在 `itzg/minecraft-server:latest`，安装脚本会跳过代理预拉取。

Example (manual proxy pull):
示例（手动代理拉取）：

```
sudo docker pull m.daocloud.io/docker.io/itzg/minecraft-server:latest
sudo docker tag m.daocloud.io/docker.io/itzg/minecraft-server:latest itzg/minecraft-server:latest
```

## Optional Web Panel / 可选 Web 面板

The panel is optional. It can be installed during deploy or added later without affecting the server.
面板是可选项，可在部署时安装，也可部署后补装，且不影响服务器本体。

### Panel prerequisites / 面板依赖

- Python packages: `fastapi`, `uvicorn`
- Frontend build output: `frontend/dist` (build with Node.js + npm)

- Python 依赖：`fastapi`, `uvicorn`
- 前端构建产物：`frontend/dist`（使用 Node.js + npm 构建）

The installer auto-builds the frontend when panel is enabled. For stability it prefers a Dockerized build (fixed Node 18).
If the panel shows a troubleshooting page, rebuild and restart:
```
docker run --rm -v /opt/mc-panel-sanitized:/app -w /app/frontend node:18 \
  sh -c "npm ci && npm run build"
systemctl restart mc-panel
```
Fallback (local npm):
```
cd /opt/mc-panel-sanitized/frontend
npm install
npm run build
systemctl restart mc-panel
```
若启用面板，安装脚本会自动构建前端。为保证稳定性，优先使用 Docker 固定 Node 18 构建。
若页面显示故障提示，请重建并重启：
```
docker run --rm -v /opt/mc-panel-sanitized:/app -w /app/frontend node:18 \
  sh -c "npm ci && npm run build"
systemctl restart mc-panel
```
兜底（本机 npm）：
```
cd /opt/mc-panel-sanitized/frontend
npm install
npm run build
systemctl restart mc-panel
```

Command input rule:
Panel commands do NOT need a leading `/`. In-game chat commands still use `/`.

指令输入规则：
面板指令不需要前置 `/`，游戏聊天中仍需 `/`。

### Install panel during deploy / 部署时安装面板

When running `install.sh`, choose:
`Install Web Panel? [y/N]`

执行 `install.sh` 时选择：
`Install Web Panel? [y/N]`

### Panel maintenance mode (existing instance) / 面板维护模式（已有实例）

`install.sh` offers a maintenance menu before deploy:

- Install panel for an existing instance
- Uninstall panel from an existing instance

`install.sh` 在部署前提供维护菜单：

- 为已有实例安装面板
- 卸载已有实例面板

The panel is a single service (`mc-panel.service`) that can manage multiple instances.
面板为单一服务（`mc-panel.service`），可管理多个实例。

### Add panel to an existing instance / 给已有实例补装面板

```
sudo python3 -m deploy.cli panel install --instance-dir /opt/mc-instances/<instance-name>
```

Options / 可选参数：

- `--panel-port 15000` to override port / 修改端口
- `--no-start` to avoid starting the service immediately / 不立即启动服务
- `--no-build` to skip frontend build / 跳过前端构建
- `--panel-root /opt/mc-panel-sanitized` to point to the repo root / 指定仓库根目录

### Uninstall panel from an instance / 从实例卸载面板

```
sudo python3 -m deploy.cli panel uninstall --instance-dir /opt/mc-instances/<instance-name>
```
## Modpack compatibility / 整合包兼容

If you provide `modpack.loader` (or `modpack.type`/`modpack.stack`) in claims params,
the planner validates it against the stack compatibility matrix. See `docs/compatibility.md`.
You can also provide `modpack.name`/`modpack.slug` to infer loader from the Modrinth top-400 index.

如果在参数中提供 `modpack.loader`（或 `modpack.type`/`modpack.stack`），
Planner 会按兼容矩阵校验，详见 `docs/compatibility.md`。
也可提供 `modpack.name`/`modpack.slug` 从 Modrinth Top-400 推断 loader。

## Plugin download logging / 插件下载日志

Download failures are appended to `logs/plugin_download.log`. If log push is enabled,
the deployer will attempt to push updates to the `logs` branch in the repo.

插件下载失败会记录到 `logs/plugin_download.log`。
若启用日志推送，部署器会尝试将更新推送到仓库 `logs` 分支。

## CLI event logging (optional) / CLI 事件日志（可选）

Set `MC_PANEL_CLI_LOG=1` to append review + execution plan events to `logs/cli_events.jsonl`.
You can override the log directory with `MC_PANEL_LOG_DIR`.

设置 `MC_PANEL_CLI_LOG=1` 可将 review 与执行计划记录到 `logs/cli_events.jsonl`。
可用 `MC_PANEL_LOG_DIR` 覆盖日志目录。

## Rules data source / 规则数据来源

Catalog/Taxonomy are stored in the external rules repository.
Catalog/Taxonomy 存放在外部规则仓库。

- https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/catalog/vanilla_1.21.4.json
- https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/taxonomy/vanilla_1.21.4.json

## Memory format / 内存格式

`docker.env.MEMORY` accepts integers or decimals (e.g. `2G`, `2.5G`).
Decimals are normalized to MB before starting the server to avoid JVM errors.

`docker.env.MEMORY` 支持整数或小数（如 `2G`, `2.5G`）。
小数会自动转换为 MB 再启动服务器，避免 JVM 参数报错。


---

## RELEASE_DRAFT_v1.0.0.md

﻿# MC Panel v1.0.0 / v1.0.0 发布草案

This release marks the first stable, publishable version of the Minecraft Configuration Decision Engine with an optional runtime panel.
这是 Minecraft 配置裁决引擎的首个可发布稳定版本，包含可选运行期面板。

AI Usage Notice / AI 使用说明
This project was developed by a single person (freshman year). Due to limited time and technical resources, AI assistance was heavily used throughout the implementation.
本项目由单人（大一）完成，受限于时间与技术资源，开发过程中大量使用 AI 辅助。

Highlights / 亮点
- Rules-driven planning: catalog + taxonomy + planner -> allow/warn/block/recommend.
- Loader: pulls rules from the remote rules repository.
- Execution Plan (dry-run): deterministic, auditable plan output.
- Claims string: params-only import/export.
- Optional runtime panel: FastAPI backend + React frontend.

- 规则驱动规划：catalog + taxonomy + planner -> allow/warn/block/recommend。
- Loader：从远端规则仓库拉取规则。
- 执行计划（dry-run）：确定性、可审计。
- Claims 字符串：仅 params 的导入/导出。
- 可选运行期面板：FastAPI 后端 + React 前端。

Key Features / 核心功能
- Review output: warnings, blocks, recommendations.
- CLI: plan/apply (dry-run default), instances listing, panel install/uninstall.
- Panel: metrics, logs, command/RCON, players, map tiles, rules editor, inventory (via optional plugin).
- Map plugins: Dynmap/BlueMap optional support, config reload via RCON.
- Plugin download logging with optional git push to logs branch.

- Review 输出：warnings / blocks / recommendations。
- CLI：plan/apply（默认 dry-run）、实例列表、面板安装/卸载。
- 面板：指标、日志、命令/RCON、玩家、地图瓦片、规则编辑、背包（可选插件）。
- 地图插件：Dynmap/BlueMap 可选支持，RCON 重载配置。
- 插件下载日志：可选推送到仓库 logs 分支。

Notes / 说明
- Panel is optional and can be installed later.
- This release does not auto-apply recommendations or execute system changes by default.

- 面板为可选项，可部署后补装。
- 本版本不会自动应用推荐或执行系统更改。

If you want to verify locally / 本地验证
```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/demon1.1/install.sh | sudo bash
```


---

## RELEASE_DRAFT_v1.0.1.md

﻿# MC Panel v1.0.1 / v1.0.1 补丁说明

This patch release fixes deploy flow issues reported after v1.0.0.
本补丁版本修复 v1.0.0 后反馈的部署流程问题。

AI Usage Notice / AI 使用说明
This project was developed by a single person (freshman year). Due to limited time and technical resources, AI assistance was heavily used throughout the implementation.
本项目由单人（大一）完成，受限于时间与技术资源，开发过程中大量使用 AI 辅助。

Fixes / 修复
- Language selection added at the start of install flow.
- Minecraft version input is now a menu + validated custom entry.
- Map plugin choice validates download URL; failed option no longer proceeds.
- Blocked plan now allows interactive adjustments before exit.
- Player-scope block rule relaxed to warn with recommendations (e.g., allow-flight).

- 安装流程开始处加入语言选择。
- 版本输入改为菜单 + 校验的自定义输入。
- 地图插件下载链接可达性校验，失败不继续。
- plan 被 block 后允许交互式调整再继续。
- 玩家范围参数从 block 调整为 warn + 推荐（如 allow-flight）。

Quick start / 快速开始
```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/v1.0.1/install.sh | sudo bash
```


---

## RELEASE_DRAFT_v1.0.2.md

﻿Highlights / 亮点
Inventory UI now supports full Chinese item names via official zh_cn.json.
背包物品中文名全量覆盖（官方 zh_cn.json）。
Owner panel with per-instance owners.json and owner-only controls.
服主栏支持实例级 owners.json，仅服主可管理。
Map preview embeds BlueMap (port 8100) with a direct open button.
地图预览内嵌 8100 端口 BlueMap，并提供“打开详细地图”按钮。
Inventory editing supports offline playerdata and online RCON replace.
支持离线 NBT 读取与在线 RCON 写入背包。
Inventory shows armor/offhand slots and keeps hotbar at the bottom.
背包支持盔甲/副手槽位，快捷栏固定在最底行。
Added permanent ban actions with a dedicated banned-players list.
新增永久封禁按钮与封禁玩家栏（移出即解封）。

Technical Notes / 技术说明
This release focuses on stability and practical operator features.
本次更新以稳定性与实用运维功能为主。
Because time/effort is limited, a significant portion was assisted by AI.
由于时间与精力有限，本次更新中大量使用了 AI 辅助。

Notes / 备注
If you encounter errors, copy the error output + this release note and ask an AI for help.
如遇报错，请将报错与本说明一并复制给可接触的 AI，通常能快速定位问题。

Acknowledgements / 致谢
Thanks to MRBHZ, Galetta_886, tsien666, and Long_Huangei for helping with testing.
感谢 MRBHZ、Galetta_886、tsien666、Long_Huangei 在测试期间的支持与帮助。


---

## RELEASE_NOTES.md

﻿# MC Panel v1.0.0 Release Notes / v1.0.0 发布说明

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
