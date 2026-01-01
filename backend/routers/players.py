from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.auth import get_current_user
from backend.models import PlayerInfo, PlayerInventoryResponse, PlayerInventoryUpdateRequest
from backend.routers.instances import resolve_instance_dir
from backend.runtime.player_tracker import get_session_seconds
from backend.runtime.rcon_client import RCONClient

router = APIRouter()


@router.get("/api/players")
def players_endpoint(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    instance_dir = instance_dir or resolve_instance_dir()
    client = RCONClient.from_instance_dir(instance_dir)
    names = client.list_players()
    log_path = Path(instance_dir) / "logs" / "latest.log"
    players = []
    for name in names:
        position = client.get_player_position(name)
        session_seconds = get_session_seconds(log_path, name)
        players.append(
            PlayerInfo(
                name=name,
                uuid=name,
                skin_url=f"https://mc-heads.net/avatar/{name}",
                session_seconds=session_seconds,
                position=position,
            )
        )
    return players


@router.get("/api/players/inventory", response_model=PlayerInventoryResponse)
def player_inventory(name: str = Query(...), instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    instance_dir = instance_dir or resolve_instance_dir()
    plugins_dir = Path(instance_dir) / "data" / "plugins"
    supported = plugins_dir.exists() and any(plugins_dir.iterdir())
    if not supported:
        return PlayerInventoryResponse(
            player=name,
            supported=False,
            items=[],
            message="Inventory editing requires a compatible plugin.",
        )
    return PlayerInventoryResponse(
        player=name,
        supported=False,
        items=[],
        message="Inventory editing plugin not wired yet.",
    )


@router.post("/api/players/inventory", response_model=PlayerInventoryResponse)
def update_player_inventory(payload: PlayerInventoryUpdateRequest, user=Depends(get_current_user)):
    raise HTTPException(status_code=409, detail="Inventory editing is not available yet.")
