from __future__ import annotations

import json
from pathlib import Path

from backend.runtime.instance_paths import instance_child
from backend.runtime.rcon_client import RCONClient


def _banlist_path(instance_dir: str) -> Path:
    return instance_child(instance_dir, "data", "banned-players.json")


def _read_banlist(instance_dir: str) -> list[dict]:
    path = _banlist_path(instance_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        return data
    return []


def list_bans(instance_dir: str) -> list[dict]:
    bans = _read_banlist(instance_dir)
    bans.sort(key=lambda item: item.get("name") or "")
    return bans


def ban_player(instance_dir: str, name: str, reason: str | None = None) -> list[dict]:
    client = RCONClient.from_instance_dir(instance_dir)
    command = f"ban {name}" if not reason else f"ban {name} {reason}"
    client.execute(command)
    return list_bans(instance_dir)


def unban_player(instance_dir: str, name: str) -> list[dict]:
    client = RCONClient.from_instance_dir(instance_dir)
    client.execute(f"pardon {name}")
    return list_bans(instance_dir)
