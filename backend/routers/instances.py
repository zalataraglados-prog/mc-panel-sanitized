import os
from pathlib import Path

from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from deploy.executor.host_inspector import HostInspector
from backend.runtime.cache import TTLCache
from backend.models import InstancesResponse

router = APIRouter()
_INSTANCES_CACHE = TTLCache(ttl_seconds=5.0)

DEFAULT_BASE_DIR = "/opt/mc-instances"


def resolve_instance_dir(base_dir: str = DEFAULT_BASE_DIR) -> str:
    """
    Pick the first instance directory if available, otherwise the base dir.
    """
    override = os.environ.get("MC_PANEL_INSTANCE_DIR")
    if override:
        return override
    base_dir = os.environ.get("MC_PANEL_BASE_DIR", base_dir)
    if not Path(base_dir).exists():
        return base_dir
    inspector = HostInspector()
    result = inspector.list_instances(base_dir)
    if result.get("ok") and result.get("instances"):
        return result["instances"][0]["path"]
    return base_dir


@router.get("/api/instances", response_model=InstancesResponse)
def instances_endpoint(base_dir: str = DEFAULT_BASE_DIR, user=Depends(get_current_user)):
    base_dir = os.environ.get("MC_PANEL_BASE_DIR", base_dir)
    cache_key = base_dir
    cached = _INSTANCES_CACHE.get(cache_key)
    if cached:
        return InstancesResponse(instances=cached)
    inspector = HostInspector()
    result = inspector.list_instances(base_dir)
    if not result.get("ok"):
        return InstancesResponse(instances=[])
    instances = result.get("instances", [])
    _INSTANCES_CACHE.set(cache_key, instances)
    return InstancesResponse(instances=instances)
