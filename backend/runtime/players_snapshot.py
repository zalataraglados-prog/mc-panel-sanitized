from __future__ import annotations

import json
import threading

from backend.runtime.cache import TTLCache
from backend.runtime.instance_paths import instance_child
from backend.runtime.log_paths import resolve_latest_log
from backend.runtime.player_tracker import get_session_seconds
from backend.runtime.rcon_client import RCONClient

_PLAYERS_CACHE = TTLCache(ttl_seconds=1.0)
_LOCKS_GUARD = threading.Lock()
_INSTANCE_LOCKS: dict[str, threading.Lock] = {}


def _get_instance_lock(instance_dir: str) -> threading.Lock:
    with _LOCKS_GUARD:
        lock = _INSTANCE_LOCKS.get(instance_dir)
        if lock is None:
            lock = threading.Lock()
            _INSTANCE_LOCKS[instance_dir] = lock
        return lock

def _load_usercache(instance_dir: str) -> list[dict]:
    path = instance_child(instance_dir, "data", "usercache.json")
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
    path = instance_child(instance_dir, "owners.json")
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

def _avatar_url(name: str, uuid: str) -> str:
    safe_name = name.strip()
    safe_uuid = uuid.strip()
    if safe_name:
        return f"https://minotar.net/avatar/{safe_name}/64"
    if safe_uuid and "-" in safe_uuid:
        return f"https://crafatar.com/avatars/{safe_uuid}?size=64&overlay"
    return "https://minotar.net/avatar/steve/64"

def get_players_snapshot(instance_dir: str) -> list[dict]:
    cached = _PLAYERS_CACHE.get(instance_dir)
    if cached is not None:
        return cached

    # Prevent thundering-herd recomputes when cache expires under high concurrency.
    with _get_instance_lock(instance_dir):
        cached = _PLAYERS_CACHE.get(instance_dir)
        if cached is not None:
            return cached

        client = RCONClient.from_instance_dir(instance_dir)
        names = client.list_players()
        online_set = {_normalize_name(name) for name in names}
        usercache = _load_usercache(instance_dir)
        uuid_map = {
            _normalize_name(entry.get("name") or ""): (entry.get("uuid") or "")
            for entry in usercache
            if entry.get("name")
        }
        owner_names = _load_owner_names(instance_dir)
        log_path = resolve_latest_log(instance_dir)
        players: list[dict] = []
        for name in names:
            position = client.get_player_position(name)
            session_seconds = get_session_seconds(log_path, name)
            mapped_uuid = uuid_map.get(_normalize_name(name)) or name
            players.append(
                {
                    "name": name,
                    "uuid": mapped_uuid,
                    "skin_url": _avatar_url(name, mapped_uuid),
                    "session_seconds": session_seconds,
                    "position": position,
                    "online": True,
                    "last_seen": None,
                    "role": "owner" if _normalize_name(name) in owner_names else None,
                }
            )

        for entry in usercache:
            name = entry.get("name") or ""
            uuid = entry.get("uuid") or ""
            expires_on = entry.get("expiresOn")
            if not name or _normalize_name(name) in online_set:
                continue
            mapped_uuid = uuid or name
            players.append(
                {
                    "name": name,
                    "uuid": mapped_uuid,
                    "skin_url": _avatar_url(name, mapped_uuid),
                    "session_seconds": 0,
                    "position": {"x": 0.0, "y": 0.0, "z": 0.0},
                    "online": False,
                    "last_seen": expires_on,
                    "role": "owner" if _normalize_name(name) in owner_names else None,
                }
            )

        _PLAYERS_CACHE.set(instance_dir, players)
        return players
