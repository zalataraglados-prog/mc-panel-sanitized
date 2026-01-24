from __future__ import annotations

import json
from pathlib import Path

from backend.runtime.cache import TTLCache
from backend.runtime.log_paths import resolve_latest_log
from backend.runtime.player_tracker import get_session_seconds
from backend.runtime.rcon_client import RCONClient

_PLAYERS_CACHE = TTLCache(ttl_seconds=3.0)

def _load_usercache(instance_dir: str) -> list[dict]:
    path = Path(instance_dir) / "data" / "usercache.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        return data
    return []


def _load_owner_names(instance_dir: str) -> set[str]:
    path = Path(instance_dir) / "owners.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return set()
    if isinstance(data, list):
        return {_normalize_name(str(name)) for name in data if str(name).strip()}
    return set()

def _normalize_name(name: str) -> str:
    return name.strip().lower()

def get_players_snapshot(instance_dir: str) -> list[dict]:
    cached = _PLAYERS_CACHE.get(instance_dir)
    if cached is not None:
        return cached

    client = RCONClient.from_instance_dir(instance_dir)
    names = client.list_players()
    online_set = {_normalize_name(name) for name in names}
    owner_names = _load_owner_names(instance_dir)
    log_path = resolve_latest_log(instance_dir)
    players: list[dict] = []
    for name in names:
        position = client.get_player_position(name)
        session_seconds = get_session_seconds(log_path, name)
        players.append(
            {
                "name": name,
                "uuid": name,
                "skin_url": f"https://mc-heads.net/avatar/{name}",
                "session_seconds": session_seconds,
                "position": position,
                "online": True,
                "last_seen": None,
                "role": "owner" if _normalize_name(name) in owner_names else None,
            }
        )

    for entry in _load_usercache(instance_dir):
        name = entry.get("name") or ""
        uuid = entry.get("uuid") or ""
        expires_on = entry.get("expiresOn")
        if not name or _normalize_name(name) in online_set:
            continue
        players.append(
            {
                "name": name,
                "uuid": uuid or name,
                "skin_url": f"https://mc-heads.net/avatar/{name or uuid}",
                "session_seconds": 0,
                "position": {"x": 0.0, "y": 0.0, "z": 0.0},
                "online": False,
                "last_seen": expires_on,
                "role": "owner" if _normalize_name(name) in owner_names else None,
            }
        )

    _PLAYERS_CACHE.set(instance_dir, players)
    return players
