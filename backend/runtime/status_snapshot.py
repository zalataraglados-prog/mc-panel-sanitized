from __future__ import annotations

from datetime import datetime

from backend.runtime.cache import TTLCache
from backend.runtime.mc_client import MCClient
from backend.runtime.metrics import gather_metrics
from backend.runtime.rcon_client import RCONClient

_STATUS_CACHE = TTLCache(ttl_seconds=10.0)


def get_status_snapshot(instance_dir: str) -> dict:
    cached = _STATUS_CACHE.get(instance_dir)
    if cached is not None:
        return cached

    metrics = gather_metrics(instance_dir)
    running = MCClient(instance_dir).status().get("running", False)
    rcon_client = RCONClient.from_instance_dir(instance_dir)
    rcon_ok = False
    rcon_message = "RCON disabled"
    if rcon_client.enabled:
        response = rcon_client.execute("list")
        rcon_ok = bool(response) and not response.startswith("RCON ")
        rcon_message = response
    payload = {
        "running": bool(running),
        "players": metrics["players"],
        "tps": metrics["tps"],
        "mspt": metrics["mspt"],
        "ping": metrics["ping"],
        "cpu_usage": metrics["cpu"],
        "memory_usage": metrics["memory"],
        "disk_usage": metrics["disk"],
        "rcon_ok": rcon_ok,
        "rcon_message": rcon_message,
        "instance_dir": instance_dir,
        "updated_at": datetime.utcnow(),
    }
    _STATUS_CACHE.set(instance_dir, payload)
    return payload
