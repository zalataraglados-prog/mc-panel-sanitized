from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user
from backend.models import MetricsPoint
from backend.runtime import metrics as runtime_metrics
from backend.routers.instances import resolve_instance_dir

router = APIRouter()
history = []


@router.get("/api/metrics")
def metrics_endpoint(window: int = Query(60, ge=10, le=300), user=Depends(get_current_user)):
    instance_dir = resolve_instance_dir()
    point = runtime_metrics.gather_metrics(instance_dir)
    history.append({"timestamp": point["timestamp"], "value": point["tps"]})
    # keep only window worth of data
    history[:] = history[-window:]
    return [MetricsPoint(timestamp=p["timestamp"], value=p["value"]) for p in history]
