from __future__ import annotations

import json
from pathlib import Path

from backend.runtime.instance_paths import instance_child

def _owners_path(instance_dir: str) -> Path:
    return instance_child(instance_dir, "owners.json")


def read_owners(instance_dir: str) -> list[str]:
    path = _owners_path(instance_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    owners: list[str] = []
    seen = set()
    for name in data:
        if not isinstance(name, str):
            continue
        value = name.strip()
        key = value.lower()
        if not value or key in seen:
            continue
        seen.add(key)
        owners.append(value)
    return owners


def write_owners(instance_dir: str, owners: list[str]) -> list[str]:
    normalized: list[str] = []
    seen = set()
    for name in owners:
        if not isinstance(name, str):
            continue
        value = name.strip()
        key = value.lower()
        if not value or key in seen:
            continue
        seen.add(key)
        normalized.append(value)
    path = _owners_path(instance_dir)
    path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    return normalized
