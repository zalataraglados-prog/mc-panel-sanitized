from fastapi import APIRouter, Depends, Query, Response

from backend.auth import get_current_user, require_roles
from backend.models import MapConfigFile, MapConfigResponse, MapStatusResponse
from backend.routers.instances import resolve_instance_dir
from backend.runtime.map_provider import get_map_status, resolve_tile_path

router = APIRouter()


@router.get("/api/map/status", response_model=MapStatusResponse)
def map_status(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    target_dir = instance_dir or resolve_instance_dir()
    status = get_map_status(target_dir)
    return MapStatusResponse(
        source=status.source,
        available=status.available,
        y_min=status.y_min,
        y_max=status.y_max,
        supports_y=status.supports_y,
    )


@router.get("/api/map/tile")
def map_tile(
    dimension: str = Query("overworld"),
    x: int = Query(0),
    z: int = Query(0),
    zoom: int = Query(0, ge=0, le=6),
    y: int = Query(64),
    instance_dir: str | None = Query(None),
    user=Depends(get_current_user),
):
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    target_dir = instance_dir or resolve_instance_dir()
    path = resolve_tile_path(target_dir, dimension, x, z, zoom, y)
    if path and path.exists():
        return Response(path.read_bytes(), media_type="image/png")

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="512" height="512">
      <rect width="100%" height="100%" fill="#0f172a"/>
      <text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle" fill="#94a3b8" font-size="20">
        No tile
      </text>
      <text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle" fill="#94a3b8" font-size="14">
        {dimension} x={x} z={z} y={y} z={zoom}
      </text>
    </svg>
    """.strip()
    return Response(svg, media_type="image/svg+xml")


@router.get("/api/map/config", response_model=MapConfigResponse)
def map_config(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    target_dir = instance_dir or resolve_instance_dir()
    base = Path(target_dir) / "data" / "plugins"
    dynmap_dir = base / "dynmap"
    bluemap_dir = base / "BlueMap"
    files: list[MapConfigFile] = []
    plugin = None
    if (dynmap_dir / "configuration.txt").exists():
        plugin = "dynmap"
        files.append(
            MapConfigFile(
                name="configuration.txt",
                content=(dynmap_dir / "configuration.txt").read_text(encoding="utf-8", errors="ignore"),
            )
        )
    if (bluemap_dir / "core.conf").exists():
        plugin = "bluemap"
        for name in (
            "core.conf",
            "webserver.conf",
            "webapp.conf",
            "plugin.conf",
            "maps/map.conf",
            "storages/file.conf",
            "storages/sql.conf",
        ):
            path = bluemap_dir / name
            if path.exists():
                files.append(MapConfigFile(name=name, content=path.read_text(encoding="utf-8", errors="ignore")))
    return MapConfigResponse(plugin=plugin, files=files)
