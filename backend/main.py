import os
from typing import Iterable
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.logging import get_logger
from backend.routers.command import router as command_router
from backend.routers.control import router as control_router
from backend.routers.instances import router as instances_router
from backend.routers.logs import router as logs_router
from backend.routers.map import router as map_router
from backend.routers.metrics import router as metrics_router
from backend.routers.players import router as players_router
from backend.routers.owners import router as owners_router
from backend.routers.bans import router as bans_router
from backend.routers.rcon import router as rcon_router
from backend.routers.status import router as status_router
from backend.routers.summary import router as summary_router
from backend.routers.auth import router as auth_router
from backend.routers.claims import router as claims_router
from backend.routers.rules import router as rules_router
from backend.routers.templates import router as templates_router
from backend.routers.users import router as users_router
from backend.routers.resourcepacks import router as resourcepacks_router

app = FastAPI(title="MC-Panel Runtime API")
app.include_router(auth_router)
app.include_router(claims_router)
app.include_router(status_router)
app.include_router(summary_router)
app.include_router(metrics_router)
app.include_router(logs_router)
app.include_router(map_router)
app.include_router(command_router)
app.include_router(control_router)
app.include_router(rcon_router)
app.include_router(players_router)
app.include_router(owners_router)
app.include_router(bans_router)
app.include_router(instances_router)
app.include_router(rules_router)
app.include_router(templates_router)
app.include_router(users_router)
app.include_router(resourcepacks_router)

_TRAILING_PATH_CHARS = "”\"’‘。．，、；：!！?？）)]}"

def _strip_trailing_path_chars(path: str) -> str:
    cleaned = path
    while cleaned and cleaned[-1] in _TRAILING_PATH_CHARS:
        cleaned = cleaned[:-1]
    return cleaned


@app.middleware("http")
async def normalize_request_path(request: Request, call_next):
    path = request.url.path
    cleaned = _strip_trailing_path_chars(path)
    if cleaned != path:
        scope = request.scope
        scope["path"] = cleaned
        scope["raw_path"] = cleaned.encode()
        request = Request(scope, request.receive)
    return await call_next(request)

def _static_candidates() -> Iterable[Path]:
    env_dir = os.environ.get("MC_PANEL_STATIC_DIR")
    if env_dir:
        yield Path(env_dir)
    yield Path("/opt/mc-panel-sanitized/frontend/dist")
    yield Path(__file__).resolve().parents[1] / "frontend" / "dist"


def _mount_static() -> None:
    logger = get_logger("backend.static")
    for candidate in _static_candidates():
        index_path = candidate / "index.html"
        if candidate.exists() and index_path.exists():
            app.mount("/", StaticFiles(directory=candidate, html=True), name="panel")
            logger.info("Mounted panel static dir: %s", candidate)
            return
        logger.info("Static candidate missing: %s (index=%s)", candidate, index_path)
    logger.warning("No panel static dir mounted; serving fallback HTML.")

    @app.get("/", include_in_schema=False)
    async def panel_fallback():
        return HTMLResponse(_FALLBACK_HTML)



_FALLBACK_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>MC Panel</title>
  <style>
    body { font-family: system-ui, Segoe UI, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }
    .wrap { max-width: 820px; margin: 40px auto; padding: 24px; }
    .card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 18px; }
    code { background: #0b1220; padding: 2px 6px; border-radius: 6px; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h2>Panel UI not built</h2>
      <p>The frontend build failed or npm is not available.</p>
      <p>Run:</p>
      <pre><code>cd /opt/mc-panel-sanitized/frontend
npm install
npm run build</code></pre>
      <hr/>
      <h2>面板前端未构建</h2>
      <p>前端构建失败或未安装 npm。</p>
      <p>请执行：</p>
      <pre><code>cd /opt/mc-panel-sanitized/frontend
npm install
npm run build</code></pre>
    </div>
  </div>
</body>
</html>
"""

_mount_static()
