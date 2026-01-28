# MC Panel (demon1.3)

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

## Quick start (plan + dry-run) / 快速开始（仅 plan + dry-run）

```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/demon1.3/install.sh | sudo bash
```

After the first install, you can run the short command below (Linux only):
??????????????????? Linux??

```
mcic
```

## Network resilience / 网络可靠性

The installer retries external HTTP fetches with backoff to survive flaky networks.
安装脚本对外部请求自动重试并指数退避，减少因网络波动导致的失败。

Optional environment variables:
可选环境变量：

- `MC_PANEL_HTTP_RETRIES` (default 3) / 重试次数
- `MC_PANEL_HTTP_BACKOFF_SECONDS` (default 2) / 初始退避秒数

### Docker mirror & proxy pull / Docker 镜像加速与代理拉取

If Docker Hub is unreachable, the installer can prompt for a mirror or a proxy prefix:
当 Docker Hub 不可达时，安装脚本会提示你配置镜像加速或代理前缀：

- Mirror prompt (writes `/etc/docker/daemon.json`, restarts Docker)
- Proxy pull prompt (pre-pulls via proxy and tags locally)

Environment variables (skip prompts):
环境变量（跳过交互）：

- `MC_PANEL_DOCKER_MIRRORS` (comma-separated, e.g. `https://a.mirror,https://b.mirror`)
- `MC_PANEL_DOCKER_MIRROR` (legacy single mirror, still supported)
- `MC_PANEL_DOCKER_PROXY_PREFIX` (e.g. `m.daocloud.io/docker.io`)

If `itzg/minecraft-server:latest` already exists locally, the installer skips the proxy prompt.
若本地已存在 `itzg/minecraft-server:latest`，安装脚本会跳过代理提示。

Example (manual proxy pull):
示例（手动代理拉取）：

```
sudo docker pull m.daocloud.io/docker.io/itzg/minecraft-server:latest
sudo docker tag m.daocloud.io/docker.io/itzg/minecraft-server:latest itzg/minecraft-server:latest
```

### Multi-mirror fallback / 多镜像源兜底

Docker will try registry mirrors in order; configure multiple mirrors to improve resilience.
Docker 会按顺序尝试镜像源；配置多个镜像源能提升成功率。

The mirror prompt also accepts multiple comma-separated URLs.
镜像提示同样支持多个逗号分隔的地址。

```
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{"registry-mirrors":["https://mirror-a.example.com","https://mirror-b.example.com"]}
EOF
sudo systemctl restart docker
```

## Optional Web Panel / 可选 Web 面板

The panel is optional. It can be installed during deploy or added later without affecting the server.
面板是可选项，可在部署时安装，也可部署后补装，且不影响服务器本体。

### Panel prerequisites / 面板依赖

- Python packages: `fastapi`, `uvicorn`
- Frontend build output: `frontend/dist` (build with Node.js + npm)

- Python 依赖：`fastapi`, `uvicorn`
- 前端构建产物：`frontend/dist`（使用 Node.js + npm 构建）

The installer auto-builds the frontend when panel is enabled and npm is available.
若启用面板且 npm 可用，安装脚本会自动构建前端。

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

## Map plugins / 地图插件

During deploy, you can optionally enable Dynmap or BlueMap. The deployer can configure:
部署时可选 Dynmap 或 BlueMap，部署器可配置：

- plugin port (`map.plugin_port`) / 插件端口
- render interval (`map.render_interval`) / 渲染间隔
- optional world file copy (`map.file`, `map.target`, `map.overwrite`) / 可选世界文件导入

### BlueMap (Paper required) / BlueMap（需要 Paper）

If `map.plugin=bluemap` is selected, the deployer forces `docker.env.TYPE=PAPER` to ensure plugin loading.
BlueMap requires accepting resource download in `core.conf` and will not render until it has generated tiles.
The deployer sets `accept-download: true` by default.

如果选择 `map.plugin=bluemap`，部署器会强制 `docker.env.TYPE=PAPER` 以确保插件可加载。
BlueMap 需要在 `core.conf` 中允许资源下载，生成瓦片后才会渲染。
部署器默认设置 `accept-download: true`。

The panel shows a live preview by embedding the external BlueMap viewer (port 8100),
and provides a button to open the detailed map in a new window.
面板内嵌 8100 端口的 BlueMap 页面作为预览，并提供按钮打开详细地图。

If BlueMap has no tiles yet, run:
`bluemap render world` (panel/RCON) or `/bluemap render world` (in-game).

若 BlueMap 尚未生成瓦片，请执行：
`bluemap render world`（面板/RCON）或 `/bluemap render world`（游戏内）。

## Inventory plugins / 背包插件

During deploy, you can optionally install an inventory plugin for richer inventory editing.
Supported choices: InvSee++ or OpenInv. Defaults point to the `vanilla_catalog` repository, but you can override the URL.

部署时可选安装背包插件用于更丰富的背包编辑。
支持：InvSee++ 或 OpenInv。默认下载源指向 `vanilla_catalog` 仓库，也可覆盖 URL。

### Offline inventory editing / 离线背包编辑

If OpenInv is installed and the player has joined at least once (so `usercache.json` exists),
the panel can read/write the offline inventory directly from `world/playerdata/*.dat`.
Online players are still handled via RCON.

若安装 OpenInv 且玩家至少进入过一次（存在 `usercache.json`），
面板可直接读取/写入 `world/playerdata/*.dat`。
在线玩家仍通过 RCON 处理。

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
