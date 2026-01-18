import os
from typing import Iterable
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.routers.command import router as command_router
from backend.routers.control import router as control_router
from backend.routers.instances import router as instances_router
from backend.routers.logs import router as logs_router
from backend.routers.map import router as map_router
from backend.routers.metrics import router as metrics_router
from backend.routers.players import router as players_router
from backend.routers.rcon import router as rcon_router
from backend.routers.status import router as status_router
from backend.routers.summary import router as summary_router
from backend.routers.auth import router as auth_router
from backend.routers.claims import router as claims_router
from backend.routers.rules import router as rules_router
from backend.routers.templates import router as templates_router
from backend.routers.users import router as users_router

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
app.include_router(instances_router)
app.include_router(rules_router)
app.include_router(templates_router)
app.include_router(users_router)

def _static_candidates() -> Iterable[Path]:
    env_dir = os.environ.get("MC_PANEL_STATIC_DIR")
    if env_dir:
        yield Path(env_dir)
    yield Path("/opt/mc-panel-sanitized/frontend/dist")
    yield Path(__file__).resolve().parents[1] / "frontend" / "dist"


def _mount_static() -> None:
    for candidate in _static_candidates():
        index_path = candidate / "index.html"
        if candidate.exists() and index_path.exists():
            app.mount("/", StaticFiles(directory=candidate, html=True), name="panel")
            return


_mount_static()
