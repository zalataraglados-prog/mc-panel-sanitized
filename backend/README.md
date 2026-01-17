# Web Panel Backend / 面板后端

## Prerequisites / 依赖

- Python packages: `fastapi`, `uvicorn`, `pydantic` (see `backend/requirements.txt`)
- The panel service expects `MC_PANEL_BASE_DIR` and `MC_PANEL_STATIC_DIR` set by systemd.
- Recommended: create a venv at `/opt/mc-panel-sanitized/.venv` and install requirements there.

- Python 依赖：`fastapi`, `uvicorn`, `pydantic`（见 `backend/requirements.txt`）
- 面板服务期望 systemd 设置 `MC_PANEL_BASE_DIR` 和 `MC_PANEL_STATIC_DIR`。
- 推荐：在 `/opt/mc-panel-sanitized/.venv` 创建 venv 并在其中安装依赖。

## Architecture / 结构

```
backend/
  auth.py               # simple token-role auth helpers
  logging.py            # records admin actions
  main.py               # FastAPI app wiring
  models.py             # request/response models
  routers/              # REST & WS routers
    auth.py
    status.py
    summary.py
    metrics.py
    logs.py
    command.py
    control.py
    rcon.py
    players.py
    instances.py
    rules.py
    templates.py
  runtime/              # runtime helpers for metrics/logs/RCON
    mc_client.py
    metrics.py
    inventory.py
    rcon_client.py
    log_streamer.py
```

## APIs / 接口

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/login` | exchange username/password for bearer token / 用户登录换取 token |
| `GET /api/status?instance_dir=...` | read overall metrics / 综合指标 |
| `GET /api/summary?instance_dir=...` | aggregated snapshot / 聚合快照 |
| `GET /api/metrics?window=60&instance_dir=...` | historic TPS points / TPS 历史点 |
| `GET /api/instances` | list instances / 实例列表 |
| `GET /api/map/status?instance_dir=...` | map availability / 地图可用性 |
| `GET /api/map/meta?instance_dir=...` | map meta (startLocation + maps) / 地图元信息（startLocation + 地图列表） |
| `GET /api/map/tile?dimension=...&x=...&z=...&zoom=...&y=...` | fetch map tile / 读取地图瓦片 |
| `GET /api/map/config?instance_dir=...` | read map config / 读取地图配置 |
| `PUT /api/map/config` | update map config / 写入地图配置 |
| `POST /api/map/reload?instance_dir=...` | reload map plugin / 重载地图插件 |
| `GET /api/players` | player list / 玩家列表 |
| `GET /api/players/inventory?name=...` | inventory preview / 背包预览 |
| `POST /api/players/inventory` | inventory update / 背包写入 |
| `POST /api/command` | send command / 发送指令 |
| `POST /api/control` | start/stop/restart server / 启停重启 |
| `POST /api/rcon` | send RCON / 发送 RCON |
| `GET /api/rcon/health?instance_dir=...` | RCON health / RCON 状态 |
| `GET /api/rules?instance_dir=...` | read server.properties / 读取 server.properties |
| `GET /api/claims/export?instance_dir=...` | export claims / 导出 claims |
| `GET /api/command-templates` | list templates / 模板列表 |
| `POST /api/command-templates` | add template / 新建模板 |
| `WS /api/logs/ws?token=...&instance_dir=...` | stream logs / 日志流 |

All mutating endpoints call `backend.logging.log_action` and verify roles using bearer tokens (`owner`, `admin`, `mod`, `viewer`).
所有写操作都会记录日志，并校验角色权限（`owner`, `admin`, `mod`, `viewer`）。

## Runtime / 运行时

The `runtime/` helpers wrap existing server-side logic. They currently stub metrics/log streaming and RCON; in later phases they can connect to actual Minecraft data sources.
`runtime/` 辅助模块封装服务器侧逻辑；当前为 stub，后续阶段可接入真实数据源。
