from __future__ import annotations

from pathlib import Path

from backend.runtime.instance_paths import instance_child, normalize_instance_dir


def resolve_latest_log(instance_dir: str) -> Path:
    base = normalize_instance_dir(instance_dir)
    candidates = [
        instance_child(base, "logs", "latest.log"),
        instance_child(base, "data", "logs", "latest.log"),
        instance_child(base, "logs", "console.log"),
        instance_child(base, "data", "logs", "console.log"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]
