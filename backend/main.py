from fastapi import FastAPI

from backend.routers.command import router as command_router
from backend.routers.instances import router as instances_router
from backend.routers.logs import router as logs_router
from backend.routers.metrics import router as metrics_router
from backend.routers.players import router as players_router
from backend.routers.rcon import router as rcon_router
from backend.routers.status import router as status_router
from backend.routers.auth import router as auth_router

app = FastAPI(title="MC-Panel Runtime API")
app.include_router(auth_router)
app.include_router(status_router)
app.include_router(metrics_router)
app.include_router(logs_router)
app.include_router(command_router)
app.include_router(rcon_router)
app.include_router(players_router)
app.include_router(instances_router)
