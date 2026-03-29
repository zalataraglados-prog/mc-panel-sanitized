from __future__ import annotations

import os
import shutil
import subprocess
from typing import Dict

from backend.runtime.instance_paths import normalize_instance_dir

_ALLOWED_ACTIONS = {"start", "stop", "restart"}

def _service_name(instance_dir: str) -> str:
    base = os.path.basename(str(normalize_instance_dir(instance_dir)).rstrip("/"))
    return f"{base}.service"


def control_service(instance_dir: str, action: str) -> Dict[str, str]:
    """
    Best-effort control via systemd. Returns status + details.
    """
    action = (action or "").strip().lower()
    if action not in _ALLOWED_ACTIONS:
        return {"status": "error", "details": "unsupported action"}
    if shutil.which("systemctl") is None:
        return {"status": "unavailable", "details": "systemctl not found"}

    unit = _service_name(instance_dir)
    if action == "start":
        cmd = ["systemctl", "start", "--", unit]
    elif action == "stop":
        cmd = ["systemctl", "stop", "--", unit]
    else:
        cmd = ["systemctl", "restart", "--", unit]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return {"status": f"{action} issued", "details": unit}
    except subprocess.CalledProcessError as exc:
        details = exc.stderr.strip() or exc.stdout.strip() or "systemctl failed"
        return {"status": "error", "details": details}
