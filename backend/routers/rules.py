from pathlib import Path

from fastapi import APIRouter, Depends

from backend.auth import get_current_user, require_roles
from backend.models import RuleEntry, RulesResponse
from backend.routers.instances import resolve_instance_dir

router = APIRouter()


def _read_server_properties(path: Path) -> list[RuleEntry]:
    entries: list[RuleEntry] = []
    if not path.exists():
        return entries
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        entries.append(RuleEntry(key=key.strip(), value=value.strip()))
    return entries


@router.get("/api/rules", response_model=RulesResponse)
def rules_endpoint(user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin", "mod", "viewer"])
    instance_dir = resolve_instance_dir()
    server_properties = Path(instance_dir) / "data" / "server.properties"
    entries = _read_server_properties(server_properties)
    return RulesResponse(entries=entries)
