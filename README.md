# MC Panel 

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
After the first install, you can use the short CLI (Linux only):
安装完成后可使用简写 CLI（仅 Linux）：

```
mcic
```

MCIC command dictionary (full):
MCIC 命令字典（完整版）：

Common instance flags (most commands support these):
通用实例参数（多数命令可用）：
- `--instance-dir <path>` 实例目录
- `--instance <name>` 实例名
- `--base-dir <path>` 实例根目录（默认 /opt/mc-instances）

Instance list / select:
实例管理：
- `mcic instances` 列出实例（完整路径）

Panel management:
面板管理：
- `mcic panel install` 安装面板
  - `--instance-dir <path>` 指定实例
  - `--base-dir <path>` 实例根目录
  - `--panel-port <port>` 指定面板端口
  - `--panel-root <path>` 指定面板仓库路径
  - `--no-start` 不启动服务
  - `--no-build` 跳过前端构建
- `mcic panel uninstall` 卸载面板
  - `--instance-dir <path>` 指定实例
  - `--base-dir <path>` 实例根目录

Runtime controls:
运行控制：
- `mcic up | down | restart`

Instance resolution order / 实例解析优先级
1) `--instance-dir` / `--instance`
2) 环境变量 `MCIC_INSTANCE` / `MC_PANEL_INSTANCE`
3) 自动推断唯一实例（仅在只有一个实例时）

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

