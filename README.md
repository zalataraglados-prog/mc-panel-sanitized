# MC Panel (demon1.3)

## Release Notice / 发布说明

- Important: The first two releases (v1.0.0 / v1.0.1) contain critical defects and must not be used in production.
- 重要：前两个版本（v1.0.0 / v1.0.1）存在严重缺陷，请勿用于生产环境。
- If you hit an error, copy the error output together with this README and share it with any AI you can reach; it resolves most issues quickly.
- 若遇报错，请将报错与本说明一起复制给你能接触到的 AI，通常可快速定位问题。

## Release / 版本信息

- Current release: `v1.0.2`
- Tag: `https://github.com/zalataraglados-prog/mc-panel-sanitized/releases/tag/v1.0.2`
- Notes: see `RELEASE_DRAFT_v1.0.2.md`

- 当前发布：`v1.0.2`
- 标签：`https://github.com/zalataraglados-prog/mc-panel-sanitized/releases/tag/v1.0.2`
- 说明：见 `RELEASE_DRAFT_v1.0.2.md`

This project is a configuration decision engine for Minecraft deployments with an optional runtime panel.
本项目是 Minecraft 部署的配置决策引擎，并提供可选的运行时面板。

## Quick start (plan + dry-run) / 快速开始（评审 + 预演）

```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/demon1.3/install.sh | sudo bash
```

After the first install, you can use the short CLI (Linux only):
首次安装后可使用短命令（仅 Linux）：

```
mcic
```

Instance resolution order / 实例解析顺序
1) `--instance-dir` / `--instance`
2) Env: `MCIC_INSTANCE` / `MC_PANEL_INSTANCE`
3) `~/.mcic_default` (set by `mcic use`)
4) Auto-detect when there is a single instance

## Network resilience / 网络可靠性

The installer retries external HTTP fetches with backoff to survive flaky networks.
安装器对外部下载采用退避重试，以应对网络波动。

Optional environment variables / 可选环境变量：
- `MC_PANEL_HTTP_RETRIES` (default 3)
- `MC_PANEL_HTTP_BACKOFF_SECONDS` (default 2)

## Docker mirror & proxy pull / Docker 镜像与代理

If Docker Hub is unreachable, the installer can prompt for a mirror or a proxy prefix.
当 Docker Hub 不可用时，可输入镜像源或代理前缀。

Environment variables (skip prompts) / 环境变量（跳过交互）：
- `MC_PANEL_DOCKER_MIRRORS` (comma-separated)
- `MC_PANEL_DOCKER_MIRROR` (legacy single mirror)
- `MC_PANEL_DOCKER_PROXY_PREFIX` (e.g. `m.daocloud.io/docker.io`)

If `itzg/minecraft-server:latest` already exists locally, the installer skips the proxy prompt.
若本地已有 `itzg/minecraft-server:latest`，则跳过代理预拉取提示。

Example (manual proxy pull):
```
sudo docker pull m.daocloud.io/docker.io/itzg/minecraft-server:latest
sudo docker tag m.daocloud.io/docker.io/itzg/minecraft-server:latest itzg/minecraft-server:latest
```

## Optional Web Panel / 可选 Web 面板

The panel is optional. It can be installed during deploy or added later without affecting the server.
面板为可选组件，可在部署时安装或后续补装，不影响服务器。

### Panel prerequisites / 面板依赖
- Python packages: `fastapi`, `uvicorn`
- Frontend build output: `frontend/dist` (build with Node.js + npm)

安装器在面板启用且 npm 可用时会自动构建前端。

Command input rule:
Panel commands do NOT need a leading `/`. In-game chat commands still use `/`.

### Install panel during deploy / 部署时安装面板
When running `install.sh`, choose:
`Install Web Panel? [y/N]`

### Panel maintenance mode (existing instance) / 面板维护模式（已有实例）
Use this when you already have a server and only want the panel.
如果已有服务器，只想补装面板，使用维护模式。

### Panel ports
Default panel port: 15000
Default map port: 8100

## Map / 地图

Supports BlueMap (recommended). Configure via `map.plugin` and port 8100.
支持 BlueMap（推荐），通过 `map.plugin` 与端口 8100 配置。

## Inventory / 背包

Supports InvSee (recommended) and offline NBT reading (`world/playerdata/*.dat`).
支持 InvSee（推荐）及离线 NBT 读取（`world/playerdata/*.dat`）。

## Logs / 日志

- CLI review logs (optional): `logs/cli_events.jsonl`
- Runtime logs: `logs/`

## Rules data source / 规则数据来源

Catalog/Taxonomy is defined in `docs/compatibility.md`.
规则目录在 `docs/compatibility.md`。

## Memory format / 内存格式

Memory accepts `M/G` suffixes. Decimal GB will be normalized to MB.
内存支持 `M/G` 后缀，小数 GB 会被标准化为 MB。

## License & Attribution / 许可与致谢

This project uses AI assistance in development and documentation.
本项目在开发与文档中大量使用 AI 辅助。
