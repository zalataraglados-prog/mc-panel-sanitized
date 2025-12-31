import os
import shutil
import time
from pathlib import Path


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


def gather_metrics(instance_dir: str | None = None) -> dict:
    """
    Collect host-level metrics; if instance_dir provided, disk is measured on its mount path.
    """
    disk_path = instance_dir or "/"
    if instance_dir and not Path(instance_dir).exists():
        disk_path = "/"

    cpu = _cpu_usage()
    memory = _mem_usage()
    disk = _disk_usage(disk_path)

    return {
        "timestamp": time.time(),
        "tps": 20.0,  # placeholder; real TPS should be polled from runtime hooks
        "mspt": 50.0,
        "ping": 50.0,
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "players": 0,
    }
