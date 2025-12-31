# Web Panel Backend

## Architecture

```
backend/
├── auth.py               # simple token-role auth helpers
├── logging.py            # records admin actions
├── main.py               # FastAPI app wiring
├── models.py             # request/response models
├── routers/              # REST & WS routers
│   ├── status.py
│   ├── metrics.py
│   ├── logs.py
│   ├── command.py
│   ├── rcon.py
│   ├── players.py
│   └── instances.py
└── runtime/              # runtime helpers for metrics/logs/RCON
    ├── mc_client.py
    ├── metrics.py
    ├── rcon_client.py
    ├── log_streamer.py
    └── logs.py
```

## APIs

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/login` | exchange username/password for bearer token |
| `GET /api/status` | read overall metrics (TPS/MSPT/CPU/memory/disk/players) |
| `GET /api/metrics?window=60` | return historic TPS points over window seconds |
| `GET /api/instances` | list MC instances under `/opt/mc-instances` |
| `GET /api/players` | return player list (avatar, coord, session) |
| `POST /api/command` | enqueue console or player command (owner/admin/mod) |
| `POST /api/rcon` | send custom RCON command (owner/admin) |
| `WS /api/logs/ws?token=...` | stream tail of server logs with rate limit |
| `POST /api/auth/login` | exchange username/password for bearer token |

All mutating endpoints call `backend.logging.log_action` and verify roles using bearer tokens (`owner`, `admin`, `mod`, `viewer`).

## Runtime

The `runtime/` helpers wrap existing server-side logic. They currently stub metrics/log streaming and RCON; in later phases they can connect to actual Minecraft data sources.
