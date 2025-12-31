from fastapi import APIRouter, Depends, HTTPException

from backend.auth import get_current_user, require_roles
from backend.logging import log_action

router = APIRouter()

_COMMAND_TEMPLATES = [
    {"name": "say", "command": "say Hello World"},
    {"name": "time_day", "command": "time set day"},
]


@router.get("/api/command-templates")
def list_templates(user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    return {"templates": list(_COMMAND_TEMPLATES)}


@router.post("/api/command-templates")
def add_template(payload: dict, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    name = payload.get("name")
    command = payload.get("command")
    if not name or not command:
        raise HTTPException(status_code=400, detail="Missing name/command")
    _COMMAND_TEMPLATES.append({"name": name, "command": command})
    log_action(user.username, "template_add", name)
    return {"status": "ok"}
