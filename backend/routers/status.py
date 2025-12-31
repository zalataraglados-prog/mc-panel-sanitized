from datetime import datetime
from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from backend.models import StatusResponse
from backend.runtime.metrics import gather_metrics
from backend.routers.instances import resolve_instance_dir

router = APIRouter()


@router.get("/api/status", response_model=StatusResponse)
def status_endpoint(user=Depends(get_current_user)):
    instance_dir = resolve_instance_dir()
    metrics = gather_metrics(instance_dir)
    return StatusResponse(
        running=True,
        players=metrics["players"],
        tps=metrics["tps"],
        mspt=metrics["mspt"],
        ping=metrics["ping"],
        cpu_usage=metrics["cpu"],
        memory_usage=metrics["memory"],
        disk_usage=metrics["disk"],
        instance_dir=instance_dir,
        updated_at=datetime.utcnow(),
    )
