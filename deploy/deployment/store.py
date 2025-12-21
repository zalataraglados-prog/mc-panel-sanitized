import json
from pathlib import Path
from typing import Any, Dict

from .model import Deployment


def save_deployment(deployment: Deployment, path: str):
    payload: Dict[str, Any] = deployment.to_dict()
    target = Path(path)
    target.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
