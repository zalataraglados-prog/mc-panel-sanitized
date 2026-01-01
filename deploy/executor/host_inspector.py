from __future__ import annotations

import os
import shutil
import socket
import subprocess
from typing import Any, Dict


class HostInspector:
    def check_port_free(self, port: int) -> Dict[str, Any]:
        if not isinstance(port, int):
            return {"check": "port_free", "ok": False, "details": "invalid port"}
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("0.0.0.0", port))
            return {"check": "port_free", "ok": True, "details": f"port {port} is free"}
        except OSError as exc:
            return {"check": "port_free", "ok": False, "details": str(exc)}
        finally:
            sock.close()

    def check_path_exists(self, path: str) -> Dict[str, Any]:
        ok = os.path.exists(path)
        return {"check": "path_exists", "ok": ok, "details": path}

    def check_path_writable(self, path: str) -> Dict[str, Any]:
        ok = os.access(path, os.W_OK)
        return {"check": "path_writable", "ok": ok, "details": path}

    def check_docker_available(self) -> Dict[str, Any]:
        ok = shutil.which("docker") is not None
        return {"check": "docker_available", "ok": ok, "details": "docker in PATH"}

    def check_systemd_available(self) -> Dict[str, Any]:
        ok = shutil.which("systemctl") is not None
        return {"check": "systemd_available", "ok": ok, "details": "systemctl in PATH"}

    def check_file_exists(self, path: str) -> Dict[str, Any]:
        ok = os.path.exists(path)
        return {"check": "file_exists", "ok": ok, "details": path}

    def check_service_exists(self, service_name: str) -> Dict[str, Any]:
        if not shutil.which("systemctl"):
            return {"check": "service_exists", "ok": False, "details": "systemctl missing"}
        result = subprocess.run(
            ["systemctl", "status", service_name],
            check=False,
            capture_output=True,
            text=True,
        )
        ok = result.returncode == 0
        details = service_name if ok else (result.stderr.strip() or result.stdout.strip())
        return {"check": "service_exists", "ok": ok, "details": details}

    def list_instances(self, base_dir: str) -> Dict[str, Any]:
        if not os.path.isdir(base_dir):
            return {"check": "list_instances", "ok": False, "details": "base dir missing"}
        entries = []
        for name in os.listdir(base_dir):
            path = os.path.join(base_dir, name)
            if not os.path.isdir(path):
                continue
            entries.append(
                {
                    "name": name,
                    "path": path,
                }
            )
        return {"check": "list_instances", "ok": True, "details": f"{len(entries)} instances", "instances": entries}
