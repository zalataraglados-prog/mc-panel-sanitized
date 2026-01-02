from __future__ import annotations

from pathlib import Path

from backend.runtime.cache import TTLCache
from backend.runtime.player_tracker import get_session_seconds
from backend.runtime.rcon_client import RCONClient

_PLAYERS_CACHE = TTLCache(ttl_seconds=3.0)


def get_players_snapshot(instance_dir: str) -> list[dict]:
    cached = _PLAYERS_CACHE.get(instance_dir)
    if cached is not None:
        return cached

    client = RCONClient.from_instance_dir(instance_dir)
    names = client.list_players()
    log_path = Path(instance_dir) / "logs" / "latest.log"
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
            }
        )

    _PLAYERS_CACHE.set(instance_dir, players)
    return players
