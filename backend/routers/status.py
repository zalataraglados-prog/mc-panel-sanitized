from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user
from backend.models import StatusResponse
from backend.routers.instances import resolve_instance_dir
from backend.runtime.status_snapshot import get_status_snapshot

router = APIRouter()


@router.get("/api/status", response_model=StatusResponse)
def status_endpoint(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    instance_dir = instance_dir or resolve_instance_dir()
    payload = get_status_snapshot(instance_dir)
    return StatusResponse(**payload)
