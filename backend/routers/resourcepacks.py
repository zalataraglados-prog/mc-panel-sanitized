from __future__ import annotations

from fastapi import APIRouter, Depends, File, Header, Query, UploadFile
from fastapi.responses import Response

from backend.auth import get_current_user, get_user_from_optional, require_roles
from backend.routers.instances import select_instance_dir
from backend.runtime.resourcepacks import get_item_texture, resourcepack_status, upload_pack

router = APIRouter()


@router.get("/api/resourcepacks/status")
def resourcepack_status_endpoint(
    instance_dir: str | None = Query(None),
    authorization: str | None = Header(None),
    token: str | None = Query(None),
):
    user = get_user_from_optional(authorization, token)
    instance = select_instance_dir(instance_dir)
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    return resourcepack_status(instance)


@router.post("/api/resourcepacks/upload")
async def resourcepack_upload_endpoint(
    file: UploadFile = File(...),
    instance_dir: str | None = Query(None),
    user=Depends(get_current_user),
):
    require_roles(user, ["owner", "admin"])
    instance = select_instance_dir(instance_dir)
    content = await file.read()
    return upload_pack(instance, file.filename or "resourcepack.zip", content)


@router.get("/api/resourcepacks/item")
def resourcepack_item_endpoint(
    item_id: str = Query(...),
    instance_dir: str | None = Query(None),
):
    instance = select_instance_dir(instance_dir)
    texture = get_item_texture(instance, item_id)
    if not texture:
        return Response(status_code=404)
    return Response(content=texture, media_type="image/png")
