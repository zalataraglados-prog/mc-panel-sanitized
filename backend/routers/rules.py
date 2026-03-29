from pathlib import Path

from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user, require_roles
from backend.logging import log_action
from backend.models import RuleEntry, RulesResponse, RulesUpdateRequest
from backend.routers.instances import select_instance_dir
from backend.runtime.cache import TTLCache
from backend.runtime.instance_paths import instance_child

router = APIRouter()
_RULES_CACHE = TTLCache(ttl_seconds=5.0)


def _read_server_properties(path: Path) -> list[RuleEntry]:
    entries: list[RuleEntry] = []
    if not path.exists():
        return entries
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        entries.append(RuleEntry(key=key.strip(), value=_clean_value(value)))
    return entries


def _clean_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _safe_instance_dir(value: str | None) -> str:
    return select_instance_dir(value)


@router.get("/api/rules", response_model=RulesResponse)
def rules_endpoint(instance_dir: str | None = Query(None), user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    instance_dir = _safe_instance_dir(instance_dir)
    server_properties = instance_child(instance_dir, "data", "server.properties")
    cache_key = str(server_properties)
    cached = _RULES_CACHE.get(cache_key)
    if cached:
        return RulesResponse(entries=cached)
    entries = _read_server_properties(server_properties)
    _RULES_CACHE.set(cache_key, entries)
    return RulesResponse(entries=entries)


@router.put("/api/rules", response_model=RulesResponse)
def update_rules(payload: RulesUpdateRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    instance_dir = _safe_instance_dir(payload.instance_dir)
    server_properties = instance_child(instance_dir, "data", "server.properties")
    current = {entry.key: entry.value for entry in _read_server_properties(server_properties)}
    for entry in payload.entries:
        current[entry.key] = entry.value
    lines = [f"{key}={current[key]}" for key in sorted(current.keys())]
    server_properties.parent.mkdir(parents=True, exist_ok=True)
    server_properties.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log_action(user.username, "rules_update", instance_dir)
    _RULES_CACHE.invalidate(str(server_properties))
    updated_entries = [RuleEntry(key=key, value=current[key]) for key in sorted(current.keys())]
    return RulesResponse(entries=updated_entries)
