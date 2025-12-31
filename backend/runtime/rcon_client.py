from __future__ import annotations

from pathlib import Path
from typing import List


class RCONClient:
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password

    def execute(self, command: str) -> str:
        return f"Executed: {command} (stubbed)"

    def list_players(self) -> List[str]:
        return ["player1", "player2"]

    @classmethod
    def from_instance_dir(cls, instance_dir: str) -> "RCONClient":
        props = _read_server_properties(Path(instance_dir))
        host = "localhost"
        port = int(props.get("rcon.port", "25575"))
        password = props.get("rcon.password", "change-me")
        return cls(host, port, password)


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
