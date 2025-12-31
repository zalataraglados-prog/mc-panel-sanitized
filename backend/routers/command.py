from fastapi import APIRouter, Depends

from backend.auth import get_current_user, require_roles
from backend.logging import log_action
from backend.models import CommandRequest

router = APIRouter()


@router.post("/api/command")
def command_endpoint(payload: CommandRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin", "mod"])
    log_action(user.username, "command", payload.command)
    return {"result": f"Command queued: {payload.command}"}
