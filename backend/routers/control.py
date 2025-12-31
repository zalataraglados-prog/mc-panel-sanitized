from fastapi import APIRouter, Depends, HTTPException

from backend.auth import get_current_user, require_roles
from backend.logging import log_action
from backend.models import ControlRequest

router = APIRouter()


@router.post("/api/control")
def control_endpoint(payload: ControlRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    action = payload.action.lower().strip()
    if action not in {"start", "stop", "restart"}:
        raise HTTPException(status_code=400, detail="Unsupported action")
    log_action(user.username, "control", action)
    return {"status": f"{action} requested"}
