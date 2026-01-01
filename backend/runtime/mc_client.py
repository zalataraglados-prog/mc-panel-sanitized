from __future__ import annotations

import time
from pathlib import Path
from typing import Dict

from backend.runtime.rcon_client import RCONClient


def _read_server_properties(instance_dir: Path) -> dict:
    path = instance_dir / "data" / "server.properties"
    if not path.exists():
        return {}
    result = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def _log_recent(log_path: Path, max_age_seconds: int = 300) -> bool:
    if not log_path.exists():
        return False
    age = time.time() - log_path.stat().st_mtime
    return age <= max_age_seconds


class MCClient:
    def __init__(self, instance_dir: str):
        self.instance_dir = Path(instance_dir)

    def status(self) -> Dict[str, bool]:
        """
        Best-effort runtime detection using recent logs and RCON if enabled.
        """
        running = _log_recent(self.instance_dir / "logs" / "latest.log")
        props = _read_server_properties(self.instance_dir)
        rcon_enabled = props.get("enable-rcon", "false").lower() == "true"
        if rcon_enabled:
            client = RCONClient.from_instance_dir(str(self.instance_dir))
            response = client.execute("list")
            if "There are" in response:
                running = True
        return {"running": running}
