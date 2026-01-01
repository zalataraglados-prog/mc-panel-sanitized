from pathlib import Path

from backend.logging import log_action

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from backend.auth import get_current_user, require_roles
from backend.models import (
    MapConfigFile,
    MapConfigResponse,
    MapConfigUpdateRequest,
    MapReloadResponse,
    MapStatusResponse,
)
from backend.routers.instances import resolve_instance_dir
from backend.runtime.map_provider import get_map_status, resolve_tile_path
from backend.runtime.rcon_client import RCONClient

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

    if dynmap_dir.exists():
        plugin = "dynmap"
        files.extend(_collect_config_files(dynmap_dir))
    if bluemap_dir.exists():
        plugin = "bluemap"
        files.extend(_collect_config_files(bluemap_dir))

    return MapConfigResponse(plugin=plugin, files=files)


def _safe_plugin_path(base: Path, relative: str) -> Path:
    candidate = (base / relative).resolve()
    if not str(candidate).startswith(str(base.resolve())):
        raise HTTPException(status_code=400, detail="Invalid path")
    return candidate


@router.put("/api/map/config", response_model=MapConfigResponse)
def update_map_config(payload: MapConfigUpdateRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    target_dir = payload.instance_dir or resolve_instance_dir()
    base = Path(target_dir) / "data" / "plugins"
    plugin = payload.plugin
    if plugin == "dynmap":
        config_dir = base / "dynmap"
    elif plugin == "bluemap":
        config_dir = base / "BlueMap"
    else:
        raise HTTPException(status_code=400, detail="Unsupported plugin")

    allowed = {entry.name for entry in _collect_config_files(config_dir)}

    config_dir.mkdir(parents=True, exist_ok=True)
    for entry in payload.files:
        if entry.name not in allowed:
            raise HTTPException(status_code=400, detail=f"Unsupported config file: {entry.name}")
        path = _safe_plugin_path(config_dir, entry.name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(entry.content, encoding="utf-8")

    log_action(user.username, "map_config_update", plugin or "unknown")
    files = _collect_config_files(config_dir)
    return MapConfigResponse(plugin=plugin, files=files)


def _collect_config_files(base_dir: Path) -> list[MapConfigFile]:
    allowed_ext = {".txt", ".conf", ".yml", ".yaml", ".json"}
    ignore_dirs = {"tiles"}
    max_size = 512 * 1024
    items: list[MapConfigFile] = []
    if not base_dir.exists():
        return items
    for path in sorted(base_dir.rglob("*")):
        if any(part in ignore_dirs for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in allowed_ext:
            continue
        if path.stat().st_size > max_size:
            continue
        relative = path.relative_to(base_dir).as_posix()
        items.append(MapConfigFile(name=relative, content=path.read_text(encoding="utf-8", errors="ignore")))
    return items


@router.post("/api/map/reload", response_model=MapReloadResponse)
def reload_map(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    target_dir = instance_dir or resolve_instance_dir()
    base = Path(target_dir) / "data" / "plugins"
    plugin = None
    command = None
    if (base / "dynmap" / "configuration.txt").exists():
        plugin = "dynmap"
        command = "dynmap reload"
    elif (base / "BlueMap" / "core.conf").exists():
        plugin = "bluemap"
        command = "bluemap reload"

    if not command:
        raise HTTPException(status_code=404, detail="No map plugin config found")

    client = RCONClient.from_instance_dir(target_dir)
    response = client.execute(command)
    log_action(user.username, "map_reload", plugin or "unknown")
    return MapReloadResponse(plugin=plugin, status=response)
