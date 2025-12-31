from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user
from backend.models import PlayerInfo
from backend.routers.instances import resolve_instance_dir
from backend.runtime.rcon_client import RCONClient

router = APIRouter()


@router.get("/api/players")
def players_endpoint(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    instance_dir = instance_dir or resolve_instance_dir()
    client = RCONClient.from_instance_dir(instance_dir)
    names = client.list_players()
    players = []
    for name in names:
        players.append(
            PlayerInfo(
                name=name,
                uuid=name,
                skin_url=f"https://mc-heads.net/avatar/{name}",
                session_seconds=0,
                position={"x": 0.0, "y": 0.0, "z": 0.0},
            )
        )
    return players
