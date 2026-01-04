from fastapi import APIRouter, Depends

from backend.auth import get_current_user, require_roles
from backend.logging import log_action
from backend.models import CommandRequest
from backend.runtime.rcon_client import RCONClient
from backend.routers.instances import resolve_instance_dir

router = APIRouter()


@router.post("/api/rcon")
def rcon_endpoint(payload: CommandRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    instance_dir = payload.instance_dir or resolve_instance_dir()
    log_action(user.username, "rcon", payload.command)
    client = RCONClient.from_instance_dir(instance_dir)
    response = client.execute(payload.command)
    error = response.startswith("RCON ")
    return {"response": response, "ok": not error, "error": response if error else None}
