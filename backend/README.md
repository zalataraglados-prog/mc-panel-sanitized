# Web Panel Backend

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
    rcon_client.py
    log_streamer.py
```

## APIs

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/login` | exchange username/password for bearer token |
| `GET /api/status?instance_dir=...` | read overall metrics (TPS/MSPT/CPU/memory/disk/players) |
| `GET /api/metrics?window=60&instance_dir=...` | return historic TPS points over window seconds |
| `GET /api/instances` | list MC instances under `/opt/mc-instances` |
| `GET /api/players` | return player list (avatar, coord, session) |
| `POST /api/command` | enqueue console or player command (owner/admin/mod) |
| `POST /api/control` | start/stop/restart server (owner/admin) |
| `POST /api/rcon` | send custom RCON command (owner/admin) |
| `GET /api/rules?instance_dir=...` | read server.properties values |
| `GET /api/command-templates` | list command templates |
| `POST /api/command-templates` | add new template |
| `WS /api/logs/ws?token=...&instance_dir=...` | stream tail of server logs with rate limit |

All mutating endpoints call `backend.logging.log_action` and verify roles using bearer tokens (`owner`, `admin`, `mod`, `viewer`).

## Runtime

The `runtime/` helpers wrap existing server-side logic. They currently stub metrics/log streaming and RCON; in later phases they can connect to actual Minecraft data sources.
