import json
from pathlib import Path

from backend.logging import log_action

import mimetypes
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response

from backend.auth import get_current_user, get_user_from_optional, require_roles
from backend.models import (
    MapConfigFile,
    MapConfigResponse,
    MapConfigUpdateRequest,
    MapMetaResponse,
    MapReloadResponse,
    MapStatusResponse,
)
from backend.routers.instances import resolve_instance_dir
from backend.runtime.map_provider import get_map_status, resolve_tile_path
from backend.runtime.rcon_client import RCONClient

router = APIRouter()
_BLUE_MAP_WEB_INDEX = "index.html"
_BLUE_MAP_WEB_CANDIDATES = (
    Path("data") / "bluemap" / "web",
    Path("data") / "plugins" / "BlueMap" / "web",
    Path("data") / "plugins" / "BlueMap" / "bluemap" / "web",
)


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


@router.get("/api/map/meta", response_model=MapMetaResponse)
def map_meta(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    target_dir = instance_dir or resolve_instance_dir()
    base = _resolve_bluemap_web_root(Path(target_dir))
    if base is None:
        return MapMetaResponse(source=None, tile_size=None, scale=None, origin=None, start_location=None, maps=[])
    meta = _load_bluemap_meta(base)
    return MapMetaResponse(
        source="bluemap",
        tile_size=meta.get("tile_size"),
        scale=meta.get("scale"),
        origin=meta.get("origin"),
        start_location=meta.get("start_location"),
        maps=meta.get("maps") or [],
    )


@router.get("/api/map/tile")
def map_tile(
    dimension: str = Query("overworld"),
    x: int = Query(0),
    z: int = Query(0),
    zoom: int = Query(0, ge=0, le=6),
    y: int = Query(64),
    instance_dir: str | None = Query(None),
    token: str | None = Query(None),
    authorization: str | None = Header(None),
):
    user = get_user_from_optional(authorization, token)
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


@router.get("/api/map/bluemap/{path:path}")
def bluemap_web(
    path: str,
    instance_dir: str | None = Query(None),
    token: str | None = Query(None),
    authorization: str | None = Header(None),
):
    user = get_user_from_optional(authorization, token)
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    target_dir = instance_dir or resolve_instance_dir()
    base = _resolve_bluemap_web_root(Path(target_dir))
    if base is None:
        raise HTTPException(status_code=404, detail="BlueMap web not found")
    safe_path = (base / path).resolve()
    if not str(safe_path).startswith(str(base.resolve())):
        raise HTTPException(status_code=400, detail="Invalid path")
    if safe_path.is_dir():
        safe_path = safe_path / _BLUE_MAP_WEB_INDEX
    if not safe_path.exists():
        raise HTTPException(status_code=404, detail="Not found")
    media_type, _ = mimetypes.guess_type(str(safe_path))
    return Response(safe_path.read_bytes(), media_type=media_type or "application/octet-stream")


def _resolve_bluemap_web_root(instance_dir: Path) -> Path | None:
    for candidate in _BLUE_MAP_WEB_CANDIDATES:
        resolved = (instance_dir / candidate)
        if resolved.exists():
            return resolved
    return None


def _read_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None


def _load_bluemap_meta(base: Path) -> dict:
    data_dir = base / "data"
    settings_path = base / "settings.json"
    candidates = [
        data_dir / "map.json",
        data_dir / "maps.json",
        base / "maps.json",
    ]
    map_ids: list[str] = []
    map_info: dict[str, str] = {}
    meta_candidates: list[dict | list] = []
    settings_payload = _read_json(settings_path) if settings_path.exists() else None

    for path in candidates:
        if path.exists():
            payload = _read_json(path)
            if payload is not None:
                meta_candidates.append(payload)
                map_ids.extend(_extract_map_ids(payload))
                map_info.update(_extract_map_names(payload))

    if isinstance(settings_payload, dict):
        map_ids.extend(_extract_map_ids(settings_payload))
        map_info.update(_extract_map_names(settings_payload))

    for map_id in map_ids:
        for path in (
            data_dir / "maps" / f"{map_id}.json",
            data_dir / "maps" / map_id / "map.json",
            data_dir / f"{map_id}.json",
            data_dir / map_id / "map.json",
        ):
            if path.exists():
                payload = _read_json(path)
                if payload is not None:
                    meta_candidates.append(payload)
                    map_info.update(_extract_map_names(payload))

    if data_dir.exists():
        for path in data_dir.glob("*.json"):
            payload = _read_json(path)
            if payload is not None:
                meta_candidates.append(payload)

    tile_size = None
    scale = None
    origin = None
    for payload in meta_candidates:
        if tile_size is None:
            tile_size = _find_number(payload, {"tileSize", "tile_size", "tile-size", "tileSizePx"})
        if scale is None:
            scale = _find_number(payload, {"scale", "blocksPerPixel", "blockPerPixel", "tileScale", "scaleFactor"})
        if origin is None:
            origin = _find_origin(payload)
        if tile_size is not None and scale is not None and origin is not None:
            break

    start_location = None
    if isinstance(settings_payload, dict):
        start_location = settings_payload.get("startLocation") or settings_payload.get("start_location")

    maps = []
    for map_id in list(dict.fromkeys(map_ids)):
        name = map_info.get(map_id, map_id)
        maps.append({"id": map_id, "name": name})

    return {
        "tile_size": tile_size,
        "scale": scale,
        "origin": origin,
        "start_location": start_location,
        "maps": maps,
    }


def _extract_map_ids(payload: dict | list) -> list[str]:
    ids: list[str] = []
    if isinstance(payload, dict):
        items = payload.get("maps") if isinstance(payload.get("maps"), list) else payload.get("maps")
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    for key in ("id", "name", "mapId"):
                        if key in item:
                            ids.append(str(item[key]))
        elif isinstance(payload.get("maps"), dict):
            ids.extend([str(k) for k in payload.get("maps", {}).keys()])
    elif isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                for key in ("id", "name", "mapId"):
                    if key in item:
                        ids.append(str(item[key]))
    return ids


def _extract_map_names(payload: dict | list) -> dict[str, str]:
    names: dict[str, str] = {}
    if isinstance(payload, dict):
        maps = payload.get("maps")
        if isinstance(maps, list):
            for item in maps:
                if isinstance(item, dict):
                    map_id = None
                    for key in ("id", "name", "mapId"):
                        if key in item:
                            map_id = str(item[key])
                            break
                    if map_id:
                        display = item.get("displayName") or item.get("label") or item.get("name")
                        if display:
                            names[map_id] = str(display)
        elif isinstance(maps, dict):
            for map_id, value in maps.items():
                if isinstance(value, dict):
                    display = value.get("displayName") or value.get("label") or value.get("name")
                    if display:
                        names[str(map_id)] = str(display)
    elif isinstance(payload, list):
        for item in payload:
            names.update(_extract_map_names(item))
    return names


def _find_number(payload: dict | list, keys: set[str]) -> int | float | None:
    keyset = {k.lower() for k in keys}
    for key, value in _walk_payload(payload):
        if key.lower() in keyset and isinstance(value, (int, float)):
            return value
    return None


def _find_origin(payload: dict | list) -> dict | None:
    for _, value in _walk_payload(payload):
        if isinstance(value, dict):
            for pair in (("minX", "minZ"), ("originX", "originZ"), ("offsetX", "offsetZ"), ("centerX", "centerZ")):
                if pair[0] in value and pair[1] in value:
                    return {"x": float(value[pair[0]]), "z": float(value[pair[1]])}
            if "origin" in value and isinstance(value["origin"], dict):
                origin = value["origin"]
                if "x" in origin and "z" in origin:
                    return {"x": float(origin["x"]), "z": float(origin["z"])}
    return None


def _walk_payload(payload: dict | list):
    if isinstance(payload, dict):
        for key, value in payload.items():
            yield key, value
            yield from _walk_payload(value)
    elif isinstance(payload, list):
        for item in payload:
            yield from _walk_payload(item)


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
