import json
from fastapi import APIRouter, Depends, HTTPException

from backend.auth import get_current_user, require_roles
from backend.logging import log_action
from backend.models import CommandRequest, RconHealthResponse
from backend.runtime.instance_paths import instance_child, normalize_instance_dir
from backend.runtime.rcon_client import RCONClient
from backend.routers.instances import resolve_instance_dir

router = APIRouter()

_OP_LEVEL_MIN = 1
_OP_LEVEL_MAX = 4


def _rcon_public_error(response: str) -> str:
    text = (response or "").strip()
    if text.startswith("RCON "):
        return "RCON command failed"
    return text or "RCON command failed"


def _usercache_uuid(instance_dir: str, name: str) -> str | None:
    cache_path = instance_child(instance_dir, "data", "usercache.json")
    if not cache_path.exists():
        return None
    try:
        entries = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    target = name.lower()
    for entry in entries:
        if entry.get("name", "").lower() == target:
            return entry.get("uuid")
    return None


def _update_ops(instance_dir: str, name: str, level: int | None, enabled: bool) -> str | None:
    uuid = _usercache_uuid(instance_dir, name)
    if not uuid:
        return "UUID not found for player (usercache.json missing or player never joined)"
    ops_path = instance_child(instance_dir, "data", "ops.json")
    entries = []
    if ops_path.exists():
        try:
            entries = json.loads(ops_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return "Failed to read ops.json"
    entries = [entry for entry in entries if entry.get("uuid") != uuid and entry.get("name") != name]
    if enabled:
        if level is None:
            level = _OP_LEVEL_MAX
        entries.append(
            {
                "uuid": uuid,
                "name": name,
                "level": level,
                "bypassesPlayerLimit": False,
            }
        )
    try:
        ops_path.write_text(json.dumps(entries, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    except OSError:
        return "Failed to write ops.json"
    return None


def _parse_op_with_level(command: str) -> tuple[str, int] | None:
    parts = command.strip().split()
    if len(parts) == 3 and parts[0].lower() == "op" and parts[2].isdigit():
        return parts[1], int(parts[2])
    return None


def _safe_instance_dir(value: str | None) -> str:
    try:
        return str(normalize_instance_dir(value or resolve_instance_dir()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid instance dir") from exc


@router.post("/api/rcon")
def rcon_endpoint(payload: CommandRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    instance_dir = _safe_instance_dir(payload.instance_dir)
    log_action(user.username, "rcon", payload.command)
    try:
        client = RCONClient.from_instance_dir(instance_dir)
    except Exception:
        return {"response": "RCON init failed", "ok": False, "error": "rcon_init_failed"}
    parsed = _parse_op_with_level(payload.command)
    if parsed:
        name, level = parsed
        if level < _OP_LEVEL_MIN or level > _OP_LEVEL_MAX:
            return {
                "response": f"OP level must be {_OP_LEVEL_MIN}-{_OP_LEVEL_MAX}",
                "ok": False,
                "error": "invalid_op_level",
            }
        response = client.execute(f"op {name}")
        if response.startswith("RCON "):
            return {"response": response, "ok": False, "error": _rcon_public_error(response)}
        error = _update_ops(instance_dir, name, level, True)
        if error:
            return {"response": error, "ok": False, "error": error}
        return {
            "response": f"{response} (OP level set to {level})",
            "ok": True,
            "error": None,
        }
    if payload.command.strip().lower().startswith("deop "):
        name = payload.command.strip().split(maxsplit=1)[1] if len(payload.command.strip().split()) > 1 else ""
        response = client.execute(payload.command)
        if not response.startswith("RCON "):
            _update_ops(instance_dir, name, None, False)
        error = response.startswith("RCON ")
        return {"response": response, "ok": not error, "error": _rcon_public_error(response) if error else None}
    response = client.execute(payload.command)
    error = response.startswith("RCON ")
    return {"response": response, "ok": not error, "error": _rcon_public_error(response) if error else None}


@router.get("/api/rcon/health", response_model=RconHealthResponse)
def rcon_health(instance_dir: str | None = None, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    resolved = _safe_instance_dir(instance_dir)
    try:
        client = RCONClient.from_instance_dir(resolved)
    except Exception:
        return RconHealthResponse(ok=False, message="RCON init failed", instance_dir=resolved)
    if not client.enabled:
        return RconHealthResponse(ok=False, message="RCON disabled", instance_dir=resolved)
    response = client.execute("list")
    ok = bool(response) and not response.startswith("RCON ")
    return RconHealthResponse(ok=ok, message=response, instance_dir=resolved)
