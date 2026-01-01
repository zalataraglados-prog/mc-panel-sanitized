import os
from pathlib import Path

from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from deploy.executor.host_inspector import HostInspector
from backend.models import InstancesResponse

router = APIRouter()

DEFAULT_BASE_DIR = "/opt/mc-instances"


def resolve_instance_dir(base_dir: str = DEFAULT_BASE_DIR) -> str:
    """
    Pick the first instance directory if available, otherwise the base dir.
    """
    override = os.environ.get("MC_PANEL_INSTANCE_DIR")
    if override:
        return override
    if not Path(base_dir).exists():
        return base_dir
    inspector = HostInspector()
    result = inspector.list_instances(base_dir)
    if result.get("ok") and result.get("instances"):
        return result["instances"][0]["path"]
    return base_dir


@router.get("/api/instances", response_model=InstancesResponse)
def instances_endpoint(base_dir: str = DEFAULT_BASE_DIR, user=Depends(get_current_user)):
    inspector = HostInspector()
    result = inspector.list_instances(base_dir)
    if not result.get("ok"):
        return InstancesResponse(instances=[])
    return InstancesResponse(instances=result.get("instances", []))
