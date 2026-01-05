from __future__ import annotations

from pathlib import Path


def resolve_latest_log(instance_dir: str) -> Path:
    base = Path(instance_dir)
    candidates = [
        base / "logs" / "latest.log",
        base / "data" / "logs" / "latest.log",
        base / "logs" / "console.log",
        base / "data" / "logs" / "console.log",
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]
