from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from backend.runtime.cache import TTLCache
from backend.runtime.log_paths import resolve_latest_log

NETHER_MARKERS = ("the_nether", "minecraft:the_nether", "nether")
END_MARKERS = ("the_end", "minecraft:the_end", "end")


@dataclass
class MapStatus:
    source: Optional[str]
    available: Dict[str, bool]
    y_min: int
    y_max: int
    supports_y: bool


DEFAULT_Y_MIN = -64
DEFAULT_Y_MAX = 320
_MAP_STATUS_CACHE = TTLCache(ttl_seconds=3.0)


def find_map_root(instance_dir: str) -> tuple[Optional[Path], Optional[str]]:
    base = Path(instance_dir)
    candidates = [
        ("dynmap", base / "data" / "plugins" / "dynmap" / "web" / "tiles"),
        ("bluemap", base / "data" / "plugins" / "BlueMap" / "bluemap" / "web" / "maps"),
        ("bluemap", base / "data" / "plugins" / "BlueMap" / "bluemap" / "web" / "tiles"),
        ("bluemap", base / "data" / "plugins" / "BlueMap" / "web" / "maps"),
        ("bluemap", base / "data" / "plugins" / "BlueMap" / "web" / "tiles"),
        ("bluemap", base / "data" / "bluemap" / "web" / "maps"),
        ("bluemap", base / "data" / "bluemap" / "web" / "tiles"),
        ("map-tiles", base / "map-tiles"),
        ("maps", base / "maps"),
    ]
    for name, path in candidates:
        if path.exists():
            return path, name
    return None, None


def get_map_status(instance_dir: str) -> MapStatus:
    cached = _MAP_STATUS_CACHE.get(instance_dir)
    if cached:
        return cached
    root, source = find_map_root(instance_dir)
    available = {"overworld": False, "nether": False, "end": False}
    if not root:
        status = MapStatus(source=None, available=available, y_min=DEFAULT_Y_MIN, y_max=DEFAULT_Y_MAX, supports_y=False)
        _MAP_STATUS_CACHE.set(instance_dir, status)
        return status

    if source == "dynmap":
        mapping = {"overworld": ("world",), "nether": ("DIM-1",), "end": ("DIM1",)}
    elif source == "bluemap":
        mapping = {
            "overworld": ("world", "map"),
            "nether": ("world_nether", "map_nether", "the_nether"),
            "end": ("world_the_end", "map_end", "the_end"),
        }
    else:
        mapping = {"overworld": ("overworld",), "nether": ("nether",), "end": ("end",)}
    for key, folders in mapping.items():
        for folder in folders:
            if (root / folder).exists():
                available[key] = True
                break
    _apply_log_visibility(instance_dir, available)
    status = MapStatus(source=source, available=available, y_min=DEFAULT_Y_MIN, y_max=DEFAULT_Y_MAX, supports_y=True)
    _MAP_STATUS_CACHE.set(instance_dir, status)
    return status


def _apply_log_visibility(instance_dir: str, available: Dict[str, bool]) -> None:
    log_path = resolve_latest_log(instance_dir)
    if not log_path.exists():
        return
    try:
        text = log_path.read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        return
    if not available["nether"] and any(marker in text for marker in NETHER_MARKERS):
        available["nether"] = True
    if not available["end"] and any(marker in text for marker in END_MARKERS):
        available["end"] = True


def resolve_tile_path(
    instance_dir: str, dimension: str, x: int, z: int, zoom: int, y_level: int
) -> Optional[Path]:
    root, source = find_map_root(instance_dir)
    if not root:
        return None
    if source == "dynmap":
        candidates = {"overworld": ("world",), "nether": ("DIM-1",), "end": ("DIM1",)}
    elif source == "bluemap":
        candidates = {
            "overworld": ("world", "map"),
            "nether": ("world_nether", "map_nether", "the_nether"),
            "end": ("world_the_end", "map_end", "the_end"),
        }
    else:
        candidates = {"overworld": ("overworld",), "nether": ("nether",), "end": ("end",)}
    folder_candidates = candidates.get(dimension, (dimension,))
    dimension_dir = None
    for folder in folder_candidates:
        candidate = root / folder
        if candidate.exists():
            dimension_dir = candidate
            break
    if dimension_dir is None:
        dimension_dir = root / folder_candidates[0]
    if not dimension_dir.exists():
        return None
    candidates = [
        dimension_dir / f"y_{y_level}" / f"z{zoom}" / f"{x}_{z}.png",
        dimension_dir / f"y_{y_level}" / f"z_{zoom}" / f"{x}_{z}.png",
        dimension_dir / f"z{zoom}" / f"{x}_{z}.png",
        dimension_dir / f"z_{zoom}" / f"{x}_{z}.png",
        dimension_dir / f"{zoom}" / f"{x}_{z}.png",
        dimension_dir / f"{x}_{z}.png",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]
