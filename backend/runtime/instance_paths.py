from __future__ import annotations

import os
import re
from pathlib import Path


_INSTANCE_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_DEFAULT_BASE_DIR = "/opt/mc-instances"


class InstancePathError(ValueError):
    """Raised when an instance path is unsafe or invalid."""


def _base_dir() -> Path:
    return Path(os.environ.get("MC_PANEL_BASE_DIR", _DEFAULT_BASE_DIR))


def _is_base_path(raw: str, base: Path) -> bool:
    left = raw.replace("\\", "/").rstrip("/")
    right = str(base).replace("\\", "/").rstrip("/")
    return bool(left) and left == right


def _instance_name(raw: str) -> str:
    if os.path.isabs(raw) or "/" in raw or "\\" in raw:
        value = os.path.basename(raw.rstrip("/\\"))
    else:
        value = raw
    if not _INSTANCE_NAME_RE.fullmatch(value):
        raise InstancePathError("invalid instance name")
    return value


def normalize_instance_dir(instance_dir: str | Path | None) -> Path:
    """
    Normalize an instance path and keep it inside MC_PANEL_BASE_DIR.
    Accepts either absolute instance paths or plain instance names.
    """
    base = _base_dir()
    if instance_dir is None:
        override = os.environ.get("MC_PANEL_INSTANCE_DIR", "").strip()
        if override:
            if _is_base_path(override, base):
                return base
            return base / _instance_name(override)
        return base
    raw = str(instance_dir).strip()
    if not raw:
        return base
    if _is_base_path(raw, base):
        return base
    return base / _instance_name(raw)


def instance_child(instance_dir: str | Path | None, *parts: str) -> Path:
    base = normalize_instance_dir(instance_dir)
    candidate = base
    for part in parts:
        token = str(part).strip()
        if token in ("", ".", "..") or "/" in token or "\\" in token:
            raise InstancePathError("instance child path escapes base dir")
        candidate = candidate / token
    return candidate
