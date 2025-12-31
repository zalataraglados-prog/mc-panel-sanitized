from fastapi import APIRouter, Depends, HTTPException

from backend.auth import get_current_user, require_roles
from backend.logging import log_action
from backend.models import ControlRequest
from backend.routers.instances import resolve_instance_dir

router = APIRouter()


@router.post("/api/control")
def control_endpoint(payload: ControlRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    instance_dir = payload.instance_dir or resolve_instance_dir()
    action = payload.action.lower().strip()
    if action not in {"start", "stop", "restart"}:
        raise HTTPException(status_code=400, detail="Unsupported action")
    log_action(user.username, "control", f"{action}:{instance_dir}")
    return {"status": f"{action} requested", "instance_dir": instance_dir}
