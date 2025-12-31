from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from deploy.executor.host_inspector import HostInspector
from backend.models import InstancesResponse

router = APIRouter()


@router.get("/api/instances", response_model=InstancesResponse)
def instances_endpoint(base_dir: str = "/opt/mc-instances", user=Depends(get_current_user)):
    inspector = HostInspector()
    result = inspector.list_instances(base_dir)
    if not result.get("ok"):
        return InstancesResponse(instances=[])
    return InstancesResponse(instances=result.get("instances", []))
