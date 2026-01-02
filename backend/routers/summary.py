from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user, require_roles
from backend.models import MapStatusResponse, PlayerInfo, StatusResponse, SummaryResponse
from backend.routers.instances import resolve_instance_dir
from backend.runtime.map_provider import get_map_status
from backend.runtime.players_snapshot import get_players_snapshot
from backend.runtime.status_snapshot import get_status_snapshot

router = APIRouter()


@router.get("/api/summary", response_model=SummaryResponse)
def summary_endpoint(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    instance_dir = instance_dir or resolve_instance_dir()
    status_payload = get_status_snapshot(instance_dir)
    players = [PlayerInfo(**entry) for entry in get_players_snapshot(instance_dir)]
    map_status = get_map_status(instance_dir)
    return SummaryResponse(
        status=StatusResponse(**status_payload),
        players=players,
        map_status=MapStatusResponse(
            source=map_status.source,
            available=map_status.available,
            y_min=map_status.y_min,
            y_max=map_status.y_max,
            supports_y=map_status.supports_y,
        ),
    )
