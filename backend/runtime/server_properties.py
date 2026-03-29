from __future__ import annotations

from pathlib import Path

from backend.runtime.instance_paths import instance_child


def clean_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def read_server_properties(instance_dir: Path) -> dict[str, str]:
    path = instance_child(instance_dir, "data", "server.properties")
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = clean_value(value)
    return result
