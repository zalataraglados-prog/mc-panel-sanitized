import json
from pathlib import Path

from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user, require_roles
from backend.models import ClaimsExportResponse
from backend.routers.instances import resolve_instance_dir
from deploy.claims_codec import encode_claims
from deploy.loader import load_rules_bundle

router = APIRouter()


def _read_config(instance_dir: str) -> dict:
    path = Path(instance_dir) / "config.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _read_server_properties(instance_dir: str) -> dict:
    path = Path(instance_dir) / "data" / "server.properties"
    if not path.exists():
        return {}
    entries: dict = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        entries[key.strip()] = value.strip()
    return entries


def _coerce_value(value: str, dtype: str):
    if dtype == "bool":
        lowered = value.strip().lower()
        if lowered in ("true", "1", "yes", "y"):
            return True
        if lowered in ("false", "0", "no", "n"):
            return False
        return value
    if dtype == "int":
        try:
            return int(value)
        except ValueError:
            return value
    return value


def _defaults_from_catalog(catalog: dict) -> dict:
    params: dict = {}
    for section in ("server_properties", "gamerule"):
        entries = catalog.get(section, {}).get("entries", {})
        for key, meta in entries.items():
            if "default" in meta:
                params[key] = meta["default"]
    return params


@router.get("/api/claims/export", response_model=ClaimsExportResponse)
def export_claims(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    instance_dir = instance_dir or resolve_instance_dir()
    config = _read_config(instance_dir)
    mc = config.get("minecraft", {}) if isinstance(config, dict) else {}
    version = mc.get("version") or "1.21.4"
    stack_type = (mc.get("engine") or "paper").lower()

    bundle = load_rules_bundle(version)
    catalog = bundle.get("catalog", {})
    defaults = _defaults_from_catalog(catalog)

    server_props = _read_server_properties(instance_dir)
    for key, value in server_props.items():
        meta = catalog.get("server_properties", {}).get("entries", {}).get(key, {})
        default = meta.get("default")
        if isinstance(default, bool):
            dtype = "bool"
        elif isinstance(default, int):
            dtype = "int"
        else:
            dtype = "string"
        defaults[key] = _coerce_value(value, dtype)

    defaults["edition"] = "java"
    defaults["stack.type"] = stack_type
    defaults["minecraft.version"] = version

    claims_string = encode_claims(defaults)
    return ClaimsExportResponse(
        claims_string=claims_string,
        params=defaults,
        version=version,
        instance_dir=instance_dir,
    )
