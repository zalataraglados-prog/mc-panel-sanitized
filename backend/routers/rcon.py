from fastapi import APIRouter, Depends

from backend.auth import get_current_user, require_roles
from backend.logging import log_action
from backend.models import CommandRequest
from backend.runtime.rcon_client import RCONClient

router = APIRouter()


@router.post("/api/rcon")
def rcon_endpoint(payload: CommandRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    log_action(user.username, "rcon", payload.command)
    client = RCONClient("localhost", 25575, "change-me")
    response = client.execute(payload.command)
    return {"response": response}
