from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user
from backend.models import MetricsPoint
from backend.runtime import metrics as runtime_metrics
from backend.routers.instances import resolve_instance_dir

router = APIRouter()
history = []


@router.get("/api/metrics")
def metrics_endpoint(
    window: int = Query(60, ge=10, le=300),
    instance_dir: str | None = Query(None),
    user=Depends(get_current_user),
):
    target_dir = instance_dir or resolve_instance_dir()
    point = runtime_metrics.gather_metrics(target_dir)
    history.append({"timestamp": point["timestamp"], "value": point["tps"]})
    # keep only window worth of data
    history[:] = history[-window:]
    return [MetricsPoint(timestamp=p["timestamp"], value=p["value"]) for p in history]
