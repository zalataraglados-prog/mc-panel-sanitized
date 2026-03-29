from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user, require_roles
from backend.models import BanListResponse, BanUpdateRequest
from backend.routers.instances import select_instance_dir
from backend.runtime.bans import ban_player, list_bans, unban_player


router = APIRouter()


@router.get("/api/bans", response_model=BanListResponse)
def list_bans_endpoint(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    instance = select_instance_dir(instance_dir)
    return {"bans": list_bans(instance)}


@router.post("/api/bans", response_model=BanListResponse)
def ban_player_endpoint(payload: BanUpdateRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    instance = select_instance_dir(payload.instance_dir)
    return {"bans": ban_player(instance, payload.name, payload.reason)}


@router.delete("/api/bans", response_model=BanListResponse)
def unban_player_endpoint(
    name: str = Query(...), instance_dir: str | None = Query(None), user=Depends(get_current_user)
):
    require_roles(user, ["owner", "admin"])
    instance = select_instance_dir(instance_dir)
    return {"bans": unban_player(instance, name)}
