import json
from pathlib import Path
import re

from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user, require_roles
from backend.models import ClaimsExportResponse
from backend.routers.instances import resolve_instance_dir
from backend.runtime.rcon_client import RCONClient
from deploy.claims_codec import encode_claims, encode_compact, encode_minimal
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
        entries[key.strip()] = _clean_value(value)
    return entries


def _read_compose_env(instance_dir: str) -> dict:
    path = Path(instance_dir) / "docker-compose.yml"
    if not path.exists():
        return {}
    env: dict = {}
    in_env = False
    env_indent = None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not in_env and re.match(r"\s*environment:\s*$", line):
            env_indent = len(line) - len(line.lstrip())
            in_env = True
            continue
        if in_env:
            indent = len(line) - len(line.lstrip())
            if indent <= (env_indent or 0):
                in_env = False
                continue
            stripped = line.strip()
            if stripped.startswith("- " ) and "=" in stripped:
                key, value = stripped[2:].split("=", 1)
                env[key.strip()] = _clean_value(value)
    return env


def _params_from_config(config: dict) -> dict:
    if not isinstance(config, dict):
        return {}
    params: dict = {}
    mc = config.get("minecraft") if isinstance(config.get("minecraft"), dict) else {}
    if mc:
        if "version" in mc:
            params["minecraft.version"] = mc.get("version")
        if "engine" in mc:
            params["stack.type"] = str(mc.get("engine")).lower()
        jvm = mc.get("jvm") if isinstance(mc.get("jvm"), dict) else {}
        if jvm and jvm.get("memory"):
            params["docker.env.MEMORY"] = jvm.get("memory")
    panel = config.get("panel") if isinstance(config.get("panel"), dict) else {}
    if panel:
        if "enabled" in panel:
            params["panel.enable"] = panel.get("enabled")
        if "port" in panel:
            params["panel.port"] = panel.get("port")
    return params


def _params_from_compose_env(env: dict) -> dict:
    if not isinstance(env, dict):
        return {}
    params: dict = {}
    if env.get("MEMORY"):
        params["docker.env.MEMORY"] = env.get("MEMORY")
    if env.get("VERSION"):
        params["minecraft.version"] = env.get("VERSION")
    return params


def _clean_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


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


def _read_gamerules(instance_dir: str, catalog: dict) -> dict:
    entries = catalog.get("gamerule", {}).get("entries", {})
    if not entries:
        return {}
    client = RCONClient.from_instance_dir(instance_dir)
    if not client.enabled:
        return {}
    values: dict = {}
    for key in entries.keys():
        response = client.execute(f"gamerule {key}")
        if not response or response.startswith("RCON "):
            return {}
        if "No game rule" in response or "Unknown" in response:
            continue
        if ":" not in response:
            continue
        match = response.split(":")[-1].strip()
        meta = entries.get(key, {})
        default = meta.get("default")
        if isinstance(default, bool):
            parsed = _coerce_value(match, "bool")
            if isinstance(parsed, bool):
                values[key] = parsed
        elif isinstance(default, int):
            parsed = _coerce_value(match, "int")
            if isinstance(parsed, int):
                values[key] = parsed
        else:
            values[key] = match
    return values


@router.get("/api/claims/export", response_model=ClaimsExportResponse)
def export_claims(
    instance_dir: str | None = Query(None),
    format: str = Query("full", pattern="^(full|compact|min)$"),
    user=Depends(get_current_user),
):
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    instance_dir = instance_dir or resolve_instance_dir()
    config = _read_config(instance_dir)
    mc = config.get("minecraft", {}) if isinstance(config, dict) else {}
    version = mc.get("version") or "1.21.11"
    stack_type = (mc.get("engine") or "paper").lower()

    config_params = _params_from_config(config)
    compose_env = _read_compose_env(instance_dir)
    compose_params = _params_from_compose_env(compose_env)

    version = (compose_params.get("minecraft.version")
               or config_params.get("minecraft.version")
               or mc.get("version")
               or "1.21.4")

    # Avoid leaking version into extras; use version header only.
    config_params.pop("minecraft.version", None)
    compose_params.pop("minecraft.version", None)

    bundle = load_rules_bundle(version)
    catalog = bundle.get("catalog", {})
    defaults = _defaults_from_catalog(catalog)

    defaults.update(config_params)
    defaults.update(compose_params)

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

    gamerule_values = _read_gamerules(instance_dir, catalog)
    defaults.update(gamerule_values)

    defaults["stack.type"] = stack_type

    if format == "compact":
        claims_string = encode_compact(defaults, catalog, version)
    elif format == "min":
        claims_string = encode_minimal(defaults, catalog, version, template="vanilla")
    else:
        claims_string = encode_claims(defaults)
    return ClaimsExportResponse(
        claims_string=claims_string,
        params=defaults,
        version=version,
        instance_dir=instance_dir,
        format=format,
    )
