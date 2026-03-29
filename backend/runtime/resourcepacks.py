from __future__ import annotations

import io
import json
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException

from backend.runtime.cache import TTLCache
from backend.runtime.instance_paths import instance_child, normalize_instance_dir

_PACK_CACHE = TTLCache(ttl_seconds=60.0)


def _pack_root(instance_dir: str) -> Path:
    return instance_child(instance_dir, "panel", "resourcepacks")


def _current_pack_dir(instance_dir: str) -> Path:
    return _pack_root(instance_dir) / "current"


def _data_pack_dir(instance_dir: str) -> Path:
    return instance_child(instance_dir, "data", "resourcepacks")


def _collect_pack_sources(instance_dir: str) -> List[Path]:
    sources: List[Path] = []
    current_dir = _current_pack_dir(instance_dir)
    if current_dir.exists():
        sources.append(current_dir)
    data_dir = _data_pack_dir(instance_dir)
    if data_dir.exists():
        for entry in sorted(data_dir.iterdir(), reverse=True):
            if entry.is_dir() or entry.suffix.lower() == ".zip":
                sources.append(entry)
    return sources


def _index_pack_dir(base: Path) -> Dict[str, Tuple[str, Path]]:
    result: Dict[str, Tuple[str, Path]] = {}
    for texture_type in ("item", "block"):
        pattern = f"assets/*/textures/{texture_type}/*.png"
        for texture in base.rglob("*.png"):
            try:
                rel = texture.relative_to(base)
            except ValueError:
                continue
            parts = rel.parts
            if len(parts) < 5 or parts[0] != "assets":
                continue
            namespace = parts[1]
            if parts[2:4] != ("textures", texture_type):
                continue
            name = texture.stem
            item_id = f"{namespace}:{name}"
            if item_id not in result:
                result[item_id] = ("dir", texture)
    return result


def _index_pack_zip(zip_path: Path) -> Dict[str, Tuple[str, Tuple[Path, str]]]:
    result: Dict[str, Tuple[str, Tuple[Path, str]]] = {}
    try:
        with zipfile.ZipFile(zip_path) as zf:
            for name in zf.namelist():
                if not name.startswith("assets/") or not name.endswith(".png"):
                    continue
                parts = name.split("/")
                if len(parts) < 5:
                    continue
                namespace = parts[1]
                if parts[2:4] != ["textures", "item"] and parts[2:4] != ["textures", "block"]:
                    continue
                item_name = Path(name).stem
                item_id = f"{namespace}:{item_name}"
                if item_id not in result:
                    result[item_id] = ("zip", (zip_path, name))
    except zipfile.BadZipFile:
        return result
    return result


def _build_index(instance_dir: str) -> Dict[str, Tuple[str, object]]:
    normalize_instance_dir(instance_dir)
    index: Dict[str, Tuple[str, object]] = {}
    for source in _collect_pack_sources(instance_dir):
        if source.is_dir():
            for item_id, entry in _index_pack_dir(source).items():
                index.setdefault(item_id, entry)
        elif source.suffix.lower() == ".zip":
            for item_id, entry in _index_pack_zip(source).items():
                index.setdefault(item_id, entry)
    return index


def _get_index(instance_dir: str) -> Dict[str, Tuple[str, object]]:
    cached = _PACK_CACHE.get(instance_dir)
    if cached is not None:
        return cached
    index = _build_index(instance_dir)
    _PACK_CACHE.set(instance_dir, index)
    return index


def invalidate_cache(instance_dir: str) -> None:
    _PACK_CACHE.set(instance_dir, None)


def get_item_texture(instance_dir: str, item_id: str) -> Optional[bytes]:
    normalize_instance_dir(instance_dir)
    index = _get_index(instance_dir)
    entry = index.get(item_id)
    if not entry:
        return None
    source_type, payload = entry
    if source_type == "dir":
        path = payload  # type: ignore[assignment]
        try:
            return Path(path).read_bytes()
        except OSError:
            return None
    if source_type == "zip":
        zip_path, inner = payload  # type: ignore[misc]
        try:
            with zipfile.ZipFile(zip_path) as zf:
                return zf.read(inner)
        except (OSError, zipfile.BadZipFile, KeyError):
            return None
    return None


def upload_pack(instance_dir: str, filename: str, content: bytes) -> Dict[str, str]:
    normalize_instance_dir(instance_dir)
    root = _pack_root(instance_dir)
    root.mkdir(parents=True, exist_ok=True)
    zip_path = root / "uploaded.zip"
    zip_path.write_bytes(content)
    current_dir = _current_pack_dir(instance_dir)
    if current_dir.exists():
        shutil.rmtree(current_dir, ignore_errors=True)
    current_dir.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            zf.extractall(current_dir)
    except zipfile.BadZipFile as exc:
        raise HTTPException(status_code=400, detail="Invalid zip file") from exc
    invalidate_cache(instance_dir)
    return {"status": "ok", "filename": filename}


def resourcepack_status(instance_dir: str) -> Dict[str, object]:
    normalize_instance_dir(instance_dir)
    sources = _collect_pack_sources(instance_dir)
    index = _get_index(instance_dir)
    return {
        "sources": [str(source) for source in sources],
        "items": len(index),
    }
