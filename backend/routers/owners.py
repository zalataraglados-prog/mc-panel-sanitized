from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user, require_roles
from backend.models import OwnersResponse, OwnersUpdateRequest
from backend.routers.instances import select_instance_dir
from backend.runtime.owners import read_owners, write_owners

router = APIRouter()


@router.get("/api/owners", response_model=OwnersResponse)
def owners_endpoint(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    instance = select_instance_dir(instance_dir)
    return OwnersResponse(owners=read_owners(instance))


@router.put("/api/owners", response_model=OwnersResponse)
def update_owners(payload: OwnersUpdateRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner"])
    instance = select_instance_dir(payload.instance_dir)
    return OwnersResponse(owners=write_owners(instance, payload.owners))
