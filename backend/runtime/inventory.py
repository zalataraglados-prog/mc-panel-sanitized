from __future__ import annotations

import re
from pathlib import Path

from backend.runtime.rcon_client import RCONClient


PLUGIN_SIGNATURES = {
    "openinv": ("openinv", "openinv.jar"),
    "invsee": ("invsee", "invsee++.jar"),
    "essentialsx": ("essentials", "essentialsx.jar"),
}


def _read_server_properties(instance_dir: Path) -> dict:
    path = instance_dir / "data" / "server.properties"
    if not path.exists():
        return {}
    result = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def _detect_provider(instance_dir: Path) -> str | None:
    plugins_dir = instance_dir / "data" / "plugins"
    if not plugins_dir.exists():
        return None
    files = [p.name.lower() for p in plugins_dir.iterdir() if p.is_file()]
    for provider, signatures in PLUGIN_SIGNATURES.items():
        for sig in signatures:
            if any(sig in name for name in files):
                return provider
    return None


def _parse_inventory_payload(payload: str) -> list[dict]:
    items = []
    if not payload:
        return items
    if "No entity was found" in payload:
        return items
    for match in re.finditer(r"\{[^{}]*?Slot:(-?\d+)b[^{}]*?\}", payload):
        block = match.group(0)
        slot = int(match.group(1))
        id_match = re.search(r'id:"([^"]+)"', block)
        count_match = re.search(r"Count:(\d+)b", block)
        if not id_match or not count_match:
            continue
        items.append(
            {
                "slot": slot,
                "id": id_match.group(1),
                "count": int(count_match.group(1)),
            }
        )
    return items


def get_inventory(instance_dir: str, player: str) -> dict:
    instance_path = Path(instance_dir)
    provider = _detect_provider(instance_path)
    props = _read_server_properties(instance_path)
    rcon_enabled = props.get("enable-rcon", "false").lower() == "true"
    if not rcon_enabled:
        return {
            "supported": False,
            "provider": provider,
            "editable": False,
            "items": [],
            "message": "RCON disabled in server.properties",
        }

    client = RCONClient.from_instance_dir(instance_dir)
    response = client.execute(f"data get entity {player} Inventory")
    items = _parse_inventory_payload(response)
    return {
        "supported": True,
        "provider": provider or "vanilla_rcon",
        "editable": True,
        "items": items,
        "message": None if items else "No inventory data available.",
    }


def set_inventory(instance_dir: str, player: str, items: list[dict]) -> dict:
    instance_path = Path(instance_dir)
    props = _read_server_properties(instance_path)
    rcon_enabled = props.get("enable-rcon", "false").lower() == "true"
    provider = _detect_provider(instance_path)
    if not rcon_enabled:
        return {
            "supported": False,
            "provider": provider,
            "editable": False,
            "message": "RCON disabled in server.properties",
        }
    client = RCONClient.from_instance_dir(instance_dir)
    applied = 0
    for item in items:
        slot = item.get("slot")
        item_id = item.get("id")
        count = item.get("count", 1)
        if slot is None or not item_id:
            continue
        command = f"item replace entity {player} slot.inventory.{slot} {item_id} {count}"
        client.execute(command)
        applied += 1
    return {
        "supported": True,
        "provider": provider or "vanilla_rcon",
        "editable": True,
        "message": f"Applied {applied} item updates.",
    }
