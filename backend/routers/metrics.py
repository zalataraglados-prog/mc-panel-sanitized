from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user
from backend.models import MetricsPoint
from backend.routers.instances import select_instance_dir
from backend.runtime import metrics as runtime_metrics
from backend.runtime.mc_client import MCClient

router = APIRouter()
history = []


@router.get("/api/metrics")
def metrics_endpoint(
    window: int = Query(60, ge=10, le=300),
    instance_dir: str | None = Query(None),
    user=Depends(get_current_user),
):
    target_dir = select_instance_dir(instance_dir)
    if not target_dir:
        return []
    if not MCClient(target_dir).status().get("running", False):
        return []
    point = runtime_metrics.gather_metrics(target_dir)
    if point["tps"] <= 0:
        return []
    history.append({"timestamp": point["timestamp"], "value": point["tps"]})
    # keep only window worth of data
    history[:] = history[-window:]
    return [MetricsPoint(timestamp=p["timestamp"], value=p["value"]) for p in history]
