from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict


def _resolve_log_dir() -> str:
    log_dir = os.environ.get("MC_PANEL_LOG_DIR")
    if log_dir:
        return log_dir
    return os.path.join(os.getcwd(), "logs")


def log_event(event: str, payload: Dict[str, Any]) -> None:
    enabled = str(os.environ.get("MC_PANEL_CLI_LOG", "")).lower() in ("1", "true", "yes")
    if not enabled:
        return
    log_dir = _resolve_log_dir()
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "cli_events.jsonl")
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "payload": payload,
    }
    try:
        with open(log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=True))
            handle.write("\n")
    except Exception:
        return
