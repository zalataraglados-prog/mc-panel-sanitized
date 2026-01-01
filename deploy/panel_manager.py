from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from deploy.executor.host_inspector import HostInspector


DEFAULT_PANEL_PORT = 15000


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_instance_config(instance_dir: str) -> dict:
    config_path = Path(instance_dir) / "config.json"
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _resolve_instance_dir(instance_dir: str | None, base_dir: str) -> str:
    if instance_dir:
        return instance_dir
    inspector = HostInspector()
    result = inspector.list_instances(base_dir)
    if result.get("ok") and result.get("instances"):
        return result["instances"][0]["path"]
    raise RuntimeError("No instance directory found.")


def _ensure_frontend_build(repo_root: Path, build: bool) -> Path:
    dist_dir = repo_root / "frontend" / "dist"
    if (dist_dir / "index.html").exists():
        return dist_dir
    if not build:
        raise RuntimeError("Frontend build missing; run npm install && npm run build in frontend.")
    if not shutil.which("npm"):
        raise RuntimeError("npm not found; install Node.js to build the frontend.")
    subprocess.run(["npm", "install"], cwd=str(repo_root / "frontend"), check=True)
    subprocess.run(["npm", "run", "build"], cwd=str(repo_root / "frontend"), check=True)
    if not (dist_dir / "index.html").exists():
        raise RuntimeError("Frontend build failed; dist/index.html not found.")
    return dist_dir


def _ensure_panel_deps() -> None:
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
    except Exception as exc:
        raise RuntimeError("Missing FastAPI/uvicorn. Install with: pip install fastapi uvicorn") from exc


def _render_service(template_path: Path, context: dict) -> str:
    content = template_path.read_text(encoding="utf-8")
    for key, value in context.items():
        content = content.replace("{{" + key + "}}", str(value))
    return content


def install_panel(
    *,
    instance_dir: str | None,
    base_dir: str,
    panel_port: int | None,
    start: bool,
    build_frontend: bool,
    panel_root: str | None,
) -> str:
    inspector = HostInspector()
    instance_dir = _resolve_instance_dir(instance_dir, base_dir)
    instance_name = Path(instance_dir).name
    repo_root = Path(panel_root) if panel_root else _repo_root()
    _ensure_panel_deps()
    _ensure_frontend_build(repo_root, build_frontend)

    config = _load_instance_config(instance_dir)
    config_port = None
    if isinstance(config.get("panel"), dict):
        config_port = config["panel"].get("port")
    port = panel_port or config_port or DEFAULT_PANEL_PORT

    template_path = repo_root / "deploy" / "templates" / "mc-panel.service.tpl"
    if not template_path.exists():
        raise RuntimeError(f"Missing service template: {template_path}")

    service_name = f"{instance_name}-panel.service"
    service_path = Path("/etc/systemd/system") / service_name
    context = {
        "INSTANCE_NAME": instance_name,
        "INSTANCE_DIR": instance_dir,
        "PANEL_PORT": port,
        "PANEL_ROOT": str(repo_root),
        "PANEL_STATIC_DIR": str(repo_root / "frontend" / "dist"),
    }
    content = _render_service(template_path, context)
    service_path.write_text(content, encoding="utf-8")

    if not inspector.check_systemd_available().get("ok"):
        raise RuntimeError("systemd not available on this host.")

    subprocess.run(["systemctl", "daemon-reload"], check=True)
    if start:
        subprocess.run(["systemctl", "enable", "--now", service_name], check=True)
    else:
        subprocess.run(["systemctl", "enable", service_name], check=True)
    return service_name


def uninstall_panel(*, instance_dir: str | None, base_dir: str) -> str:
    inspector = HostInspector()
    instance_dir = _resolve_instance_dir(instance_dir, base_dir)
    instance_name = Path(instance_dir).name
    service_name = f"{instance_name}-panel.service"
    service_path = Path("/etc/systemd/system") / service_name

    if not inspector.check_systemd_available().get("ok"):
        raise RuntimeError("systemd not available on this host.")

    subprocess.run(["systemctl", "stop", service_name], check=False)
    subprocess.run(["systemctl", "disable", service_name], check=False)
    if service_path.exists():
        service_path.unlink()
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    return service_name
