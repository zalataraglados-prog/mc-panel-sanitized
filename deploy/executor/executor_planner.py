from __future__ import annotations

import hashlib
import json
import os
import posixpath
import socket
from typing import Any, Dict, List

from deploy.capacity_guard import capacity_status, estimate_capacity
from deploy.executor.execution_plan import Action, ExecutionPlan, Precondition


DEFAULT_BASE_DIR = "/opt/mc-instances"
DEFAULT_MC_VERSION = "1.21.4"
DEFAULT_DOCKER_IMAGE = "itzg/minecraft-server"
DEFAULT_DOCKER_TAG = "latest"
DEFAULT_PANEL_ROOT = "/opt/mc-panel-sanitized"
MAP_PLUGIN_URLS = {
    "dynmap": {
        "url": "https://dynmap.us/builds/dynmap/Dynmap-HEAD-spigot.jar",
        "filename": "Dynmap.jar",
    },
    "bluemap": {
        "url": "https://github.com/BlueMap-Minecraft/BlueMap/releases/latest/download/bluemap-5.15-spigot.jar",
        "filename": "BlueMap.jar",
    },
}
INVENTORY_PLUGIN_URLS = {
    "invsee": {
        "url": "https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/deps/plugins/invsee/InvSeePlusPlus.jar",
        "filename": "InvSeePlusPlus.jar",
    },
    "openinv": {
        "url": "https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/deps/plugins/openinv/OpenInv.jar",
        "filename": "OpenInv.jar",
    },
}


def _parse_int(value) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _parse_memory_gb(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    text = value.strip().upper()
    if text.endswith("G"):
        try:
            return float(text[:-1])
        except ValueError:
            return None
    if text.endswith("M"):
        try:
            return float(text[:-1]) / 1024
        except ValueError:
            return None
    try:
        return float(text)
    except ValueError:
        return None


def _pick_server_port(params: dict) -> int | None:
    candidates = [
        params.get("server-port"),
        params.get("minecraft.server_port"),
        params.get("network.mc_port"),
    ]
    for item in candidates:
        port = _parse_int(item)
        if port is not None:
            return port
    return None


def _needs_docker(params: dict) -> bool:
    return any(key.startswith("docker.") for key in params.keys())


def _stable_instance_name(params: dict) -> str:
    payload = json.dumps(params, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8]
    return f"instance-{digest}"


def _build_env_block(params: dict) -> str:
    lines = []
    for key, value in params.items():
        if not key.startswith("docker.env."):
            continue
        env_key = key.split(".", 2)[2]
        lines.append(f"      - {env_key}={value}")
    return "\n".join(lines)


def _build_volume_block(params: dict) -> str:
    lines = []
    for key, value in params.items():
        if not key.startswith("docker.volume."):
            continue
        mount = f"{value}"
        lines.append(f"      - {mount}")
    if not lines:
        lines = [
            "      - ./data:/data",
            "      - ./logs:/logs",
        ]
    return "\n".join(lines)


def _is_port_free(port: int, host: str = "0.0.0.0") -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def _find_free_port(start_port: int, max_tries: int = 200) -> int | None:
    port = start_port
    for _ in range(max_tries):
        if _is_port_free(port):
            return port
        port += 1
    return None


def _resolve_port(
    requested: int,
    *,
    label: str,
    notes: List[str],
    allow_fallback: bool = True,
) -> int:
    if _is_port_free(requested):
        return requested
    if not allow_fallback:
        notes.append(f"{label} port {requested} is in use")
        return requested
    resolved = _find_free_port(requested + 1)
    if resolved is None:
        notes.append(f"{label} port {requested} is in use; no free port found")
        return requested
    notes.append(f"{label} port {requested} is in use; switched to {resolved}")
    return resolved


def _build_template_context(
    params: dict,
    instance_name: str,
    instance_dir: str,
    *,
    ports: Dict[str, int] | None = None,
) -> Dict[str, Any]:
    ports = ports or {}
    mc_port = ports.get("mc_port") or _pick_server_port(params) or 25565
    panel_port = ports.get("panel_port") or _parse_int(params.get("panel.port")) or 15000
    rcon_port = ports.get("rcon_port") or _parse_int(params.get("rcon.port")) or (mc_port + 10)
    mc_version = params.get("minecraft.version", DEFAULT_MC_VERSION)
    mc_memory = params.get("docker.env.MEMORY", "2G")
    docker_image = params.get("docker.image", DEFAULT_DOCKER_IMAGE)
    docker_tag = params.get("docker.tag", DEFAULT_DOCKER_TAG)

    map_port = ports.get("map_port") or _parse_int(params.get("map.plugin_port")) or 8123
    render_interval = _parse_int(params.get("map.render_interval")) or 5
    render_interval_seconds = render_interval * 60
    panel_enabled = str(params.get("panel.enable", "false")).lower() in ("true", "1", "yes", "y")
    panel_root = os.environ.get("MC_PANEL_ROOT", DEFAULT_PANEL_ROOT)
    panel_static_dir = posixpath.join(panel_root, "frontend", "dist")

    return {
        "INSTANCE_NAME": instance_name,
        "INSTANCE_DIR": instance_dir,
        "MC_PORT": mc_port,
        "PANEL_PORT": panel_port,
        "RCON_PORT": rcon_port,
        "MC_VERSION": mc_version,
        "MC_MEMORY": mc_memory,
        "DOCKER_IMAGE": docker_image,
        "DOCKER_TAG": docker_tag,
        "RESTART_POLICY": "always",
        "ENV_BLOCK": _build_env_block(params),
        "VOLUME_BLOCK": _build_volume_block(params),
        "CREATED_AT": "1970-01-01T00:00:00Z",
        "DEPLOYER_VERSION": "phase12",
        "RCON_PASSWORD": "change-me",
        "MAP_PORT": map_port,
        "MAP_RENDER_INTERVAL": render_interval,
        "MAP_RENDER_INTERVAL_SECONDS": render_interval_seconds,
        "PANEL_ENABLED": "true" if panel_enabled else "false",
        "PANEL_ROOT": panel_root,
        "PANEL_STATIC_DIR": panel_static_dir,
    }


def _has_service(host_facts: List[Dict[str, Any]], service_name: str) -> bool:
    for fact in host_facts:
        if fact.get("check") != "service_exists":
            continue
        if fact.get("details") == service_name and fact.get("ok"):
            return True
    return False


def build_execution_plan(
    *,
    claims,
    review,
    host_facts: List[Dict[str, Any]],
    mode: str = "dry-run",
) -> ExecutionPlan:
    params = getattr(claims, "params", {}) or {}
    map_plugin = params.get("map.plugin")
    if map_plugin in ("dynmap", "bluemap") and "docker.env.TYPE" not in params:
        params = dict(params)
        params["docker.env.TYPE"] = "PAPER"
    review_level = None
    if isinstance(review, dict):
        review_level = review.get("level")
    if review_level is None:
        review_level = getattr(review, "level", None)
    if review_level is None:
        review_level = getattr(review, "summary", {}).get("level")
    review_level = review_level or "allow"

    base_dir = os.environ.get("MC_PANEL_BASE_DIR", DEFAULT_BASE_DIR)
    base_dir_parent = posixpath.dirname(base_dir.rstrip("/")) or "/"
    preconditions: List[Precondition] = [
        Precondition(type="path_exists", value=base_dir, required=False),
        Precondition(type="path_writable", value=base_dir_parent, required=True),
        Precondition(type="path_writable", value=base_dir, required=False),
        Precondition(type="systemd_pid1", value="systemd", required=False),
        Precondition(type="selinux_enforcing", value="selinux", required=False),
        Precondition(type="apparmor_enabled", value="apparmor", required=False),
        Precondition(type="ufw_active", value="ufw", required=False),
        Precondition(type="dns_configured", value="/etc/resolv.conf", required=False),
        Precondition(type="swap_available", value="swap", required=False),
        Precondition(type="disk_free", value=base_dir, required=False),
        Precondition(type="mount_noexec", value=base_dir, required=False),
        Precondition(type="time_sync", value="ntp", required=False),
        Precondition(type="ipv4_available", value="ipv4", required=False),
    ]

    port_notes: List[str] = []
    resolved_ports: Dict[str, int] = {}
    port = _pick_server_port(params) or 25565
    resolved_ports["mc_port"] = _resolve_port(port, label="MC", notes=port_notes)
    preconditions.append(
        Precondition(type="port_free", value=resolved_ports["mc_port"], required=True)
    )

    panel_enabled = str(params.get("panel.enable", "false")).lower() in ("true", "1", "yes", "y")
    panel_installed = _has_service(host_facts, "mc-panel.service")
    if panel_enabled and not panel_installed:
        panel_port = _parse_int(params.get("panel.port")) or 15000
        resolved_ports["panel_port"] = _resolve_port(panel_port, label="Panel", notes=port_notes)
        preconditions.append(
            Precondition(type="port_free", value=resolved_ports["panel_port"], required=True)
        )
        preconditions.append(Precondition(type="systemd_available", value="systemd", required=True))

    if _needs_docker(params):
        preconditions.append(Precondition(type="docker_available", value="docker", required=True))
        preconditions.append(Precondition(type="systemd_available", value="systemd", required=True))
        preconditions.append(Precondition(type="docker_rootless", value="docker", required=False))

    memory_gb = _parse_memory_gb(params.get("docker.env.MEMORY"))
    if memory_gb is not None:
        preconditions.append(Precondition(type="memory_available", value=memory_gb, required=True))

    map_file = params.get("map.file")
    if map_file:
        preconditions.append(Precondition(type="file_exists", value=map_file, required=True))

    estimate = estimate_capacity(params)
    if estimate:
        _, payload = capacity_status(estimate)
        preconditions.append(
            Precondition(
                type="capacity_sufficient",
                value=payload,
                required=True,
            )
        )

    map_plugin = params.get("map.plugin")
    if map_plugin in MAP_PLUGIN_URLS:
        map_port = _parse_int(params.get("map.plugin_port")) or 8123
        resolved_ports["map_port"] = _resolve_port(map_port, label="Map", notes=port_notes)

    rcon_port = _parse_int(params.get("rcon.port"))
    if rcon_port is None:
        rcon_port = resolved_ports["mc_port"] + 10
    if rcon_port is not None:
        resolved_ports["rcon_port"] = _resolve_port(rcon_port, label="RCON", notes=port_notes)

    instance_name = _stable_instance_name(params)
    instance_dir = posixpath.join(base_dir, instance_name)
    context = _build_template_context(params, instance_name, instance_dir, ports=resolved_ports)
    context["BASE_DIR"] = base_dir

    actions: List[Action] = [
        Action(type="mkdir", params={"path": base_dir}),
        Action(type="mkdir", params={"path": instance_dir}),
        Action(type="mkdir", params={"path": posixpath.join(instance_dir, "data")}),
        Action(type="mkdir", params={"path": posixpath.join(instance_dir, "logs")}),
        Action(
            type="write_file",
            params={
                "path": posixpath.join(instance_dir, "config.json"),
                "template": "config.json.tpl",
                "context": context,
            },
        ),
        Action(
            type="write_file",
            params={
                "path": posixpath.join(instance_dir, "docker-compose.yml"),
                "template": "docker-compose.yml.tpl",
                "context": context,
            },
        ),
        Action(
            type="write_file",
            params={
                "path": f"/etc/systemd/system/{instance_name}.service",
                "template": "minecraft.service.tpl",
                "context": context,
            },
        ),
        Action(
            type="systemd_enable_now",
            params={
                "service": f"{instance_name}.service",
                "compose_dir": instance_dir,
                "compose_service": "minecraft",
            },
        ),
    ]
    if panel_enabled:
        actions.append(
            Action(
                type="setup_panel_venv",
                params={
                    "panel_root": context["PANEL_ROOT"],
                    "requirements": ["fastapi==0.115.5", "uvicorn[standard]==0.34.0", "pydantic==2.10.4"],
                },
            )
        )
    if panel_enabled and not panel_installed:
        actions.append(
            Action(
                type="write_file",
                params={
                    "path": "/etc/systemd/system/mc-panel.service",
                    "template": "mc-panel.service.tpl",
                    "context": context,
                },
            )
        )
        actions.append(
            Action(
                type="systemd_enable_now",
                params={"service": "mc-panel.service"},
            )
        )

    if map_plugin in MAP_PLUGIN_URLS:
        plugin_spec = MAP_PLUGIN_URLS[map_plugin]
        plugin_dir = posixpath.join(instance_dir, "data", "plugins")
        plugin_target = posixpath.join(plugin_dir, plugin_spec["filename"])
        plugin_url = params.get("map.plugin_url", plugin_spec["url"])
        actions.append(Action(type="mkdir", params={"path": plugin_dir}))
        actions.append(
            Action(
                type="download_file",
                params={
                    "url": plugin_url,
                    "target": plugin_target,
                    "overwrite": False,
                },
            )
        )
        if map_plugin == "dynmap":
            actions.append(Action(type="mkdir", params={"path": posixpath.join(plugin_dir, "dynmap")}))
            actions.append(
                Action(
                    type="write_file",
                    params={
                        "path": posixpath.join(plugin_dir, "dynmap", "configuration.txt"),
                        "template": "dynmap.configuration.txt.tpl",
                        "context": context,
                    },
                )
            )
        if map_plugin == "bluemap":
            bluemap_dir = posixpath.join(plugin_dir, "BlueMap")
            actions.append(Action(type="mkdir", params={"path": bluemap_dir}))
            actions.append(Action(type="mkdir", params={"path": posixpath.join(bluemap_dir, "maps")}))
            actions.append(Action(type="mkdir", params={"path": posixpath.join(bluemap_dir, "storages")}))
            actions.append(
                Action(
                    type="write_file",
                    params={
                        "path": posixpath.join(bluemap_dir, "core.conf"),
                        "template": "bluemap.core.conf.tpl",
                        "context": context,
                    },
                )
            )
            actions.append(
                Action(
                    type="write_file",
                    params={
                        "path": posixpath.join(bluemap_dir, "webserver.conf"),
                        "template": "bluemap.webserver.conf.tpl",
                        "context": context,
                    },
                )
            )
            actions.append(
                Action(
                    type="write_file",
                    params={
                        "path": posixpath.join(bluemap_dir, "webapp.conf"),
                        "template": "bluemap.webapp.conf.tpl",
                        "context": context,
                    },
                )
            )
            actions.append(
                Action(
                    type="write_file",
                    params={
                        "path": posixpath.join(bluemap_dir, "plugin.conf"),
                        "template": "bluemap.plugin.conf.tpl",
                        "context": context,
                    },
                )
            )
            actions.append(
                Action(
                    type="write_file",
                    params={
                        "path": posixpath.join(bluemap_dir, "maps", "map.conf"),
                        "template": "bluemap.map.conf.tpl",
                        "context": context,
                    },
                )
            )
            actions.append(
                Action(
                    type="write_file",
                    params={
                        "path": posixpath.join(bluemap_dir, "storages", "file.conf"),
                        "template": "bluemap.storage.file.conf.tpl",
                        "context": context,
                    },
                )
            )
            actions.append(
                Action(
                    type="write_file",
                    params={
                        "path": posixpath.join(bluemap_dir, "storages", "sql.conf"),
                        "template": "bluemap.storage.sql.conf.tpl",
                        "context": context,
                    },
            )
        )

    inventory_plugin = params.get("inventory.plugin")
    if inventory_plugin in INVENTORY_PLUGIN_URLS:
        plugin_spec = INVENTORY_PLUGIN_URLS[inventory_plugin]
        inventory_url = params.get("inventory.plugin_url", plugin_spec.get("url"))
        if inventory_url:
            plugin_dir = posixpath.join(instance_dir, "data", "plugins")
            plugin_target = posixpath.join(plugin_dir, plugin_spec["filename"])
            actions.append(Action(type="mkdir", params={"path": plugin_dir}))
            actions.append(
                Action(
                    type="download_file",
                    params={
                        "url": inventory_url,
                        "target": plugin_target,
                        "overwrite": False,
                    },
                )
            )

    map_file = params.get("map.file")
    if map_file:
        target = posixpath.join(instance_dir, "data", params.get("map.target", "world"))
        overwrite = str(params.get("map.overwrite", "true")).lower() in ("true", "1", "yes")
        actions.append(
            Action(
                type="copy_map",
                params={
                    "source": map_file,
                    "target": target,
                    "overwrite": overwrite,
                },
            )
        )

    plan = ExecutionPlan(
        mode=mode,
        review_level=review_level,
        preconditions=preconditions,
        actions=actions,
    )
    plan.meta["resolved_ports"] = resolved_ports
    if port_notes:
        plan.meta["port_notes"] = port_notes
    plan.finalize()
    return plan
