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


def _normalize_token(value: str) -> str:
    return value.replace("\\", "/").rstrip("/")


def _list_known_instances(base_dir: str | None = None) -> list[dict]:
    inspector = HostInspector()
    previous = os.environ.get("MC_PANEL_BASE_DIR")
    if base_dir:
        os.environ["MC_PANEL_BASE_DIR"] = base_dir
    try:
        result = inspector.list_instances()
    finally:
        if base_dir:
            if previous is None:
                os.environ.pop("MC_PANEL_BASE_DIR", None)
            else:
                os.environ["MC_PANEL_BASE_DIR"] = previous
    if not result.get("ok"):
        return []
    return result.get("instances", [])


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
    instances = _list_known_instances(base_dir)
    if instances:
        return instances[0]["path"]
    return base_dir


def select_instance_dir(requested: str | None) -> str:
    default_dir = resolve_instance_dir()
    if not requested:
        return default_dir
    raw = str(requested).strip()
    token = _normalize_token(raw)
    if not token:
        return default_dir
    token_name = os.path.basename(token)
    for item in _list_known_instances():
        path = str(item.get("path") or "")
        name = str(item.get("name") or "")
        norm_path = _normalize_token(path)
        if token == norm_path or token == name or token_name == name:
            return path
    # Keep previous behavior: unknown token still uses caller-supplied path.
    return raw


@router.get("/api/instances", response_model=InstancesResponse)
def instances_endpoint(base_dir: str = DEFAULT_BASE_DIR, user=Depends(get_current_user)):
    base_dir = os.environ.get("MC_PANEL_BASE_DIR", base_dir)
    cache_key = base_dir
    cached = _INSTANCES_CACHE.get(cache_key)
    if cached:
        return InstancesResponse(instances=cached)
    instances = _list_known_instances(base_dir)
    _INSTANCES_CACHE.set(cache_key, instances)
    return InstancesResponse(instances=instances)
