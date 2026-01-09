import os
import re
import shutil
import socket
import time
from pathlib import Path

from backend.runtime.ansi import strip_ansi
from backend.runtime.cache import TTLCache
from backend.runtime.rcon_client import RCONClient

_METRICS_CACHE = TTLCache(ttl_seconds=2.0)


def _cpu_usage() -> float:
    if not hasattr(os, "getloadavg"):
        return 0.0
    load_avg = os.getloadavg()[0]
    cores = os.cpu_count() or 1
    return round(min(100.0, load_avg / cores * 100), 2)


def _mem_usage() -> float:
    mem_total = None
    mem_available = None
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemTotal:"):
                    mem_total = int(line.split()[1]) * 1024
                elif line.startswith("MemAvailable:"):
                    mem_available = int(line.split()[1]) * 1024
                if mem_total and mem_available:
                    break
    except FileNotFoundError:
        return 0.0
    if not mem_total or not mem_available:
        return 0.0
    return round((1 - mem_available / mem_total) * 100, 2)


def _disk_usage(path: str) -> float:
    disk = shutil.disk_usage(path)
    return round((disk.used / disk.total) * 100, 2) if disk.total else 0.0


def _parse_tps_response(response: str) -> tuple[float | None, float | None]:
    if not response:
        return None, None
    clean = strip_ansi(response)
    tps_list = re.search(r"TPS[^:]*:\s*([0-9.]+)(?:\s*,\s*([0-9.]+))?(?:\s*,\s*([0-9.]+))?", clean)
    mspt_list = re.search(r"MSPT[^:]*:\s*([0-9.]+)(?:\s*,\s*([0-9.]+))?(?:\s*,\s*([0-9.]+))?", clean)
    tps_match = tps_list or re.search(r"TPS[^:]*:\s*([0-9.]+)", clean)
    mspt_match = mspt_list or re.search(r"MSPT[^:]*:\s*([0-9.]+)", clean)
    tps = float(tps_match.group(1)) if tps_match else None
    mspt = float(mspt_match.group(1)) if mspt_match else None
    return tps, mspt


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


def _ping_latency(host: str, port: int, timeout: float = 1.5) -> float:
    start = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return round((time.time() - start) * 1000, 2)
    except OSError:
        return 0.0


def gather_metrics(instance_dir: str | None = None) -> dict:
    """
    Collect host-level metrics; if instance_dir provided, disk is measured on its mount path.
    """
    cache_key = instance_dir or "__host__"
    cached = _METRICS_CACHE.get(cache_key)
    if cached:
        return cached
    disk_path = instance_dir or "/"
    if instance_dir and not Path(instance_dir).exists():
        disk_path = "/"

    cpu = _cpu_usage()
    memory = _mem_usage()
    disk = _disk_usage(disk_path)

    tps = None
    mspt = None
    players = 0
    ping = 0.0

    if instance_dir and Path(instance_dir).exists():
        instance_path = Path(instance_dir)
        client = RCONClient.from_instance_dir(instance_dir)
        tps_response = client.execute("tps")
        tps, mspt = _parse_tps_response(tps_response)
        players = len(client.list_players())
        props = _read_server_properties(instance_path)
        port = int(props.get("server-port", "25565"))
        ping = _ping_latency("127.0.0.1", port)

    payload = {
        "timestamp": time.time(),
        "tps": tps if tps is not None else 0.0,
        "mspt": mspt if mspt is not None else 0.0,
        "ping": ping,
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "players": players,
    }
    _METRICS_CACHE.set(cache_key, payload)
    return payload
