# Web Panel Backend

## Prerequisites

- Python packages: `fastapi`, `uvicorn`
- The panel service expects `MC_PANEL_BASE_DIR` and `MC_PANEL_STATIC_DIR` set by systemd.

## Architecture

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

## APIs

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/login` | exchange username/password for bearer token |
| `GET /api/status?instance_dir=...` | read overall metrics (TPS/MSPT/CPU/memory/disk/players) |
| `GET /api/summary?instance_dir=...` | aggregated snapshot of status + players + map status |
| `GET /api/metrics?window=60&instance_dir=...` | return historic TPS points over window seconds |
| `GET /api/instances` | list MC instances under `/opt/mc-instances` |
| `GET /api/map/status?instance_dir=...` | report map tile availability and Y-range |
| `GET /api/map/tile?dimension=...&x=...&z=...&zoom=...&y=...` | fetch a map tile or placeholder |
| `GET /api/map/config?instance_dir=...` | read map plugin config files (dynmap/bluemap) |
| `PUT /api/map/config` | update map plugin config files |
| `POST /api/map/reload?instance_dir=...` | reload map plugin via RCON |
| `GET /api/players` | return player list (avatar, coord, session) |
| `GET /api/players/inventory?name=...` | inventory preview (RCON-based; detects plugins if present) |
| `POST /api/players/inventory` | inventory update (RCON-based; owner/admin only) |
| `POST /api/command` | enqueue console or player command (owner/admin/mod) |
| `POST /api/control` | start/stop/restart server (owner/admin) |
| `POST /api/rcon` | send custom RCON command (owner/admin) |
| `GET /api/rules?instance_dir=...` | read server.properties values |
| `GET /api/claims/export?instance_dir=...` | export claims string with defaults + current server.properties |
| `GET /api/command-templates` | list command templates |
| `POST /api/command-templates` | add new template |
| `WS /api/logs/ws?token=...&instance_dir=...` | stream tail of server logs with rate limit |

All mutating endpoints call `backend.logging.log_action` and verify roles using bearer tokens (`owner`, `admin`, `mod`, `viewer`).

## Runtime

The `runtime/` helpers wrap existing server-side logic. They currently stub metrics/log streaming and RCON; in later phases they can connect to actual Minecraft data sources.
