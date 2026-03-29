from fastapi import APIRouter, Depends

from backend.auth import get_current_user, require_roles
from backend.logging import log_action
from backend.models import CommandRequest
from backend.routers.instances import select_instance_dir
from backend.runtime.rcon_client import RCONClient

router = APIRouter()


def _rcon_public_error(response: str) -> str:
    text = (response or "").strip()
    if text.startswith("RCON "):
        return "RCON command failed"
    return text or "RCON command failed"

def _public_command_result(response: str) -> str:
    if (response or "").startswith("RCON "):
        return "RCON command failed"
    return response


def _safe_instance_dir(value: str | None) -> str:
    return select_instance_dir(value)


@router.post("/api/command")
def command_endpoint(payload: CommandRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin", "mod"])
    instance_dir = _safe_instance_dir(payload.instance_dir)
    log_action(user.username, "command", payload.command)
    try:
        client = RCONClient.from_instance_dir(instance_dir)
        response = client.execute(payload.command)
    except Exception:
        return {"result": "command failed", "ok": False, "error": "command_failed"}
    error = response.startswith("RCON ")
    return {"result": _public_command_result(response), "ok": not error, "error": _rcon_public_error(response) if error else None}
