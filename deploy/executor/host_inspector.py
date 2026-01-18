from __future__ import annotations

import os
import shutil
import socket
import subprocess
from typing import Any, Dict


class HostInspector:
    def check_memory_available(self, required_gb: float) -> Dict[str, Any]:
        if not isinstance(required_gb, (int, float)) or required_gb <= 0:
            return {"check": "memory_available", "ok": False, "details": "invalid required_gb"}
        total_kb = None
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as handle:
                for line in handle:
                    if line.startswith("MemTotal:"):
                        total_kb = int(line.split()[1])
                        break
        except FileNotFoundError:
            return {"check": "memory_available", "ok": False, "details": "meminfo not available"}
        if total_kb is None:
            return {"check": "memory_available", "ok": False, "details": "meminfo not available"}
        total_gb = total_kb / 1024 / 1024
        ok = total_gb >= float(required_gb)
        details = f"total_gb={total_gb:.2f} required_gb={float(required_gb):.2f}"
        return {"check": "memory_available", "ok": ok, "details": details}

    def check_systemd_pid1(self) -> Dict[str, Any]:
        comm_path = "/proc/1/comm"
        try:
            with open(comm_path, "r", encoding="utf-8") as handle:
                value = handle.read().strip()
        except FileNotFoundError:
            return {"check": "systemd_pid1", "ok": False, "details": "pid1 comm not available"}
        ok = value == "systemd"
        details = f"pid1={value} (systemd required for services)"
        return {"check": "systemd_pid1", "ok": ok, "details": details}

    def check_selinux_enforcing(self) -> Dict[str, Any]:
        enforce_path = "/sys/fs/selinux/enforce"
        if not os.path.exists(enforce_path):
            return {"check": "selinux_enforcing", "ok": True, "details": "selinux not present"}
        try:
            with open(enforce_path, "r", encoding="utf-8") as handle:
                value = handle.read().strip()
        except Exception:
            return {"check": "selinux_enforcing", "ok": False, "details": "unable to read enforce"}
        ok = value != "1"
        details = "enforcing (may block /opt mounts)" if value == "1" else "permissive"
        return {"check": "selinux_enforcing", "ok": ok, "details": details}

    def check_apparmor_enabled(self) -> Dict[str, Any]:
        enabled_path = "/sys/module/apparmor/parameters/enabled"
        if not os.path.exists(enabled_path):
            return {"check": "apparmor_enabled", "ok": True, "details": "apparmor not present"}
        try:
            with open(enabled_path, "r", encoding="utf-8") as handle:
                value = handle.read().strip().lower()
        except Exception:
            return {"check": "apparmor_enabled", "ok": False, "details": "unable to read apparmor status"}
        ok = value not in ("y", "yes", "1", "true")
        details = "enabled (may restrict docker/volumes)" if not ok else "disabled"
        return {"check": "apparmor_enabled", "ok": ok, "details": details}

    def check_ufw_active(self) -> Dict[str, Any]:
        if not shutil.which("ufw"):
            return {"check": "ufw_active", "ok": True, "details": "ufw not installed"}
        result = subprocess.run(
            ["ufw", "status"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        output = (result.stdout or result.stderr or "").strip()
        ok = "Status: inactive" in output
        details = output.splitlines()[0] if output else "ufw status unavailable"
        if not ok:
            details = f"{details} (ensure ports 25565/15000/8100/25575 open)"
        return {"check": "ufw_active", "ok": ok, "details": details}

    def check_dns_configured(self) -> Dict[str, Any]:
        resolv_path = "/etc/resolv.conf"
        try:
            with open(resolv_path, "r", encoding="utf-8") as handle:
                lines = [line.strip() for line in handle if line.strip()]
        except Exception:
            return {"check": "dns_configured", "ok": False, "details": "resolv.conf unreadable"}
        nameservers = [line for line in lines if line.startswith("nameserver ")]
        ok = bool(nameservers)
        details = nameservers[0] if nameservers else "no nameserver entries"
        return {"check": "dns_configured", "ok": ok, "details": details}

    def check_swap_available(self) -> Dict[str, Any]:
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as handle:
                for line in handle:
                    if line.startswith("SwapTotal:"):
                        total_kb = int(line.split()[1])
                        total_gb = total_kb / 1024 / 1024
                        ok = total_kb > 0
                        details = f"swap_total_gb={total_gb:.2f} (recommend >=1G)"
                        return {"check": "swap_available", "ok": ok, "details": details}
        except Exception:
            return {"check": "swap_available", "ok": False, "details": "swap info unavailable"}
        return {"check": "swap_available", "ok": False, "details": "swap info unavailable"}

    def check_disk_free(self, path: str, minimum_gb: float = 5.0) -> Dict[str, Any]:
        try:
            usage = shutil.disk_usage(path)
        except Exception:
            return {"check": "disk_free", "ok": False, "details": f"disk usage unavailable for {path}"}
        free_gb = usage.free / 1024 / 1024 / 1024
        ok = free_gb >= minimum_gb
        details = f"free_gb={free_gb:.2f} min_gb={minimum_gb:.2f} path={path}"
        return {"check": "disk_free", "ok": ok, "details": details}

    def check_mount_noexec(self, path: str) -> Dict[str, Any]:
        try:
            with open("/proc/mounts", "r", encoding="utf-8") as handle:
                mounts = [line.split() for line in handle if line.strip()]
        except Exception:
            return {"check": "mount_noexec", "ok": False, "details": "mount table unavailable"}
        match = None
        for entry in mounts:
            if len(entry) < 4:
                continue
            mountpoint = entry[1]
            if path.startswith(mountpoint.rstrip("/") + "/") or path == mountpoint:
                if match is None or len(mountpoint) > len(match[1]):
                    match = entry
        if match is None:
            return {"check": "mount_noexec", "ok": True, "details": "mount not found"}
        options = match[3].split(",")
        ok = "noexec" not in options
        details = f"mount={match[1]} options={match[3]} (noexec blocks services)"
        return {"check": "mount_noexec", "ok": ok, "details": details}

    def check_docker_rootless(self) -> Dict[str, Any]:
        if not shutil.which("docker"):
            return {"check": "docker_rootless", "ok": False, "details": "docker not found"}
        try:
            result = subprocess.run(
                ["docker", "info", "--format", "{{json .SecurityOptions}}"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
        except subprocess.TimeoutExpired:
            return {"check": "docker_rootless", "ok": True, "details": "docker info timed out"}
        except Exception as exc:
            return {"check": "docker_rootless", "ok": False, "details": str(exc)}
        output = (result.stdout or "").lower()
        ok = "rootless" not in output
        details = "rootless detected (low ports may fail)" if not ok else "rootless not detected"
        return {"check": "docker_rootless", "ok": ok, "details": details}

    def check_docker_daemon(self) -> Dict[str, Any]:
        if not shutil.which("docker"):
            return {"check": "docker_daemon", "ok": False, "details": "docker not found"}
        try:
            result = subprocess.run(
                ["docker", "info"],
                check=False,
                capture_output=True,
                text=True,
                timeout=8,
            )
        except subprocess.TimeoutExpired:
            return {"check": "docker_daemon", "ok": False, "details": "docker info timed out"}
        except Exception as exc:
            return {"check": "docker_daemon", "ok": False, "details": str(exc)}
        if result.returncode == 0:
            return {"check": "docker_daemon", "ok": True, "details": "docker daemon reachable"}
        details = (result.stderr or result.stdout or "").strip() or "docker daemon unavailable"
        return {"check": "docker_daemon", "ok": False, "details": details}

    def check_time_sync(self) -> Dict[str, Any]:
        if not shutil.which("timedatectl"):
            return {"check": "time_sync", "ok": False, "details": "timedatectl missing"}
        result = subprocess.run(
            ["timedatectl", "show", "-p", "NTPSynchronized", "--value"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        value = (result.stdout or "").strip().lower()
        ok = value == "yes"
        details = f"ntp_sync={value or 'unknown'}"
        return {"check": "time_sync", "ok": ok, "details": details}

    def check_ipv4_available(self) -> Dict[str, Any]:
        if shutil.which("ip"):
            result = subprocess.run(
                ["ip", "-4", "addr"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = result.stdout or ""
            ok = "inet " in output
            details = "ipv4 detected" if ok else "no ipv4 addr"
            return {"check": "ipv4_available", "ok": ok, "details": details}
        try:
            infos = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
        except Exception:
            return {"check": "ipv4_available", "ok": False, "details": "no ipv4 addr"}
        ok = bool(infos)
        details = "ipv4 detected" if ok else "no ipv4 addr (ipv6-only host?)"
        return {"check": "ipv4_available", "ok": ok, "details": details}
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
