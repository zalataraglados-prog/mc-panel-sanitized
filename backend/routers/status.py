from datetime import datetime
from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from backend.models import StatusResponse
from backend.runtime.metrics import gather_metrics

router = APIRouter()


@router.get("/api/status", response_model=StatusResponse)
def status_endpoint(user=Depends(get_current_user)):
    metrics = gather_metrics()
    return StatusResponse(
        running=True,
        players=metrics["players"],
        tps=metrics["tps"],
        mspt=metrics["mspt"],
        ping=metrics["ping"],
        cpu_usage=metrics["cpu"],
        memory_usage=metrics["memory"],
        disk_usage=metrics["disk"],
        instance_dir="/opt/mc-instances/instance-xyz",
        updated_at=datetime.utcnow(),
    )
