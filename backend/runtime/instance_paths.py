from __future__ import annotations

import os
import re
from pathlib import Path


_INSTANCE_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_DEFAULT_BASE_DIR = "/opt/mc-instances"


class InstancePathError(ValueError):
    """Raised when an instance path is unsafe or invalid."""


def _base_dir() -> Path:
    return Path(os.environ.get("MC_PANEL_BASE_DIR", _DEFAULT_BASE_DIR)).resolve()


def _allowed_roots() -> list[Path]:
    roots = [_base_dir()]
    override = os.environ.get("MC_PANEL_INSTANCE_DIR", "").strip()
    if override:
        roots.append(Path(override).resolve())
    return roots


def normalize_instance_dir(instance_dir: str | Path | None) -> Path:
    """
    Normalize an instance path and keep it inside MC_PANEL_BASE_DIR.
    Accepts either absolute instance paths or plain instance names.
    """
    base = _base_dir()
    if instance_dir is None:
        return base
    raw = str(instance_dir).strip()
    if not raw:
        return base
    if os.path.isabs(raw):
        candidate = Path(raw).resolve()
    else:
        if not _INSTANCE_NAME_RE.fullmatch(raw):
            raise InstancePathError("invalid instance name")
        candidate = (base / raw).resolve()
    for root in _allowed_roots():
        try:
            candidate.relative_to(root)
            return candidate
        except ValueError:
            continue
    raise InstancePathError("instance path escapes base dir")
    return candidate


def instance_child(instance_dir: str | Path | None, *parts: str) -> Path:
    base = normalize_instance_dir(instance_dir)
    candidate = (base.joinpath(*parts)).resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise InstancePathError("instance child path escapes base dir") from exc
    return candidate
