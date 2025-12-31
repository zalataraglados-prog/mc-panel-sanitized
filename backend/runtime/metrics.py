import os
import shutil
import time


def gather_metrics() -> dict:
    load_avg = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0

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
        pass

    memory_usage = 0.0
    if mem_total and mem_available:
        memory_usage = round((1 - mem_available / mem_total) * 100, 2)

    disk = shutil.disk_usage("/")
    disk_usage = round((disk.used / disk.total) * 100, 2) if disk.total else 0.0

    return {
        "timestamp": time.time(),
        "tps": round(load_avg, 2),
        "mspt": round(1000 / (load_avg or 1), 2) if load_avg else 0.0,
        "ping": round(load_avg * 10, 2),
        "cpu": round(load_avg / (os.cpu_count() or 1) * 100, 2),
        "memory": memory_usage,
        "disk": disk_usage,
        "players": 0,
    }
