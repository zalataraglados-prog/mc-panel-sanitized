from fastapi import APIRouter, Depends, HTTPException, Query

from backend.auth import get_current_user, require_roles
from backend.models import PlayerInfo, PlayerInventoryResponse, PlayerInventoryUpdateRequest
from backend.routers.instances import resolve_instance_dir
from backend.runtime.inventory import get_inventory, set_inventory
from backend.runtime.players_snapshot import get_players_snapshot

router = APIRouter()


@router.get("/api/players")
def players_endpoint(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    instance_dir = instance_dir or resolve_instance_dir()
    players = get_players_snapshot(instance_dir)
    return [PlayerInfo(**entry) for entry in players]


@router.get("/api/players/inventory", response_model=PlayerInventoryResponse)
def player_inventory(name: str = Query(...), instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin", "mod"])
    instance_dir = instance_dir or resolve_instance_dir()
    result = get_inventory(instance_dir, name)
    return PlayerInventoryResponse(player=name, **result)


@router.post("/api/players/inventory", response_model=PlayerInventoryResponse)
def update_player_inventory(payload: PlayerInventoryUpdateRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    instance_dir = payload.instance_dir or resolve_instance_dir()
    result = set_inventory(instance_dir, payload.player, [item.model_dump() for item in payload.items])
    if not result.get("supported"):
        raise HTTPException(status_code=409, detail=result.get("message") or "Inventory update not supported.")
    return PlayerInventoryResponse(player=payload.player, **result)
