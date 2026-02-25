from __future__ import annotations

import time
from pathlib import Path
from typing import Dict

from backend.runtime.log_paths import resolve_latest_log
from backend.runtime.rcon_client import RCONClient
from backend.runtime.server_properties import read_server_properties


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
        log_path = resolve_latest_log(str(self.instance_dir))
        running = False
        props = read_server_properties(self.instance_dir)
        rcon_enabled = props.get("enable-rcon", "false").lower() == "true"
        if rcon_enabled:
            client = RCONClient.from_instance_dir(str(self.instance_dir))
            response = client.execute("list")
            if response and not response.startswith("RCON "):
                running = True
            else:
                running = _log_recent(log_path)
        else:
            running = _log_recent(log_path)
        return {"running": running}
