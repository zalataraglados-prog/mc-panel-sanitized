from __future__ import annotations

import re
from pathlib import Path

import json
from backend.runtime.nbt import TAG_BYTE, TAG_COMPOUND, TAG_LIST, TAG_STRING, read_nbt, write_nbt
from backend.runtime.rcon_client import RCONClient


PLUGIN_SIGNATURES = {
    "openinv": ("openinv", "openinv.jar"),
    "invsee": ("invsee", "invsee++.jar", "invseeplusplus.jar"),
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
        result[key.strip()] = _clean_value(value)
    return result


def _clean_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


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


def _load_usercache(instance_dir: Path) -> dict:
    path = instance_dir / "data" / "usercache.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return {}
    mapping = {}
    for entry in data:
        name = entry.get("name")
        uuid = entry.get("uuid")
        if name and uuid:
            mapping[name] = uuid
    return mapping


def _resolve_player_uuid(instance_dir: Path, player: str) -> str | None:
    usercache = _load_usercache(instance_dir)
    for name, uuid in usercache.items():
        if name.lower() == player.lower():
            return uuid
    return None


def _resolve_playerdata(instance_dir: Path, player: str) -> Path | None:
    usercache = _load_usercache(instance_dir)
    uuid = usercache.get(player)
    if not uuid:
        return None
    playerdata = instance_dir / "data" / "world" / "playerdata" / f"{uuid}.dat"
    if playerdata.exists():
        return playerdata
    return None


def _extract_inventory_list(root: dict) -> list[dict]:
    if root.get("type") != TAG_COMPOUND:
        return []
    compound = root.get("value", {})
    inv_tag = compound.get("Inventory")
    if not inv_tag or inv_tag.get("type") != TAG_LIST:
        return []
    inv_value = inv_tag.get("value", {})
    if inv_value.get("item_type") != TAG_COMPOUND:
        return []
    return inv_value.get("items", [])


def _inventory_items_from_tags(items: list[dict]) -> list[dict]:
    result = []
    for entry in items:
        if not isinstance(entry, dict):
            continue
        slot_tag = entry.get("Slot")
        id_tag = entry.get("id")
        count_tag = entry.get("Count")
        if not slot_tag or not id_tag or not count_tag:
            continue
        result.append(
            {
                "slot": int(slot_tag["value"]),
                "id": id_tag["value"],
                "count": int(count_tag["value"]),
            }
        )
    return result


def _update_inventory_tags(items: list[dict], desired: list[dict]) -> list[dict]:
    existing_by_slot = {}
    for entry in items:
        slot_tag = entry.get("Slot")
        if slot_tag:
            existing_by_slot[int(slot_tag["value"])] = entry

    updated = []
    for item in desired:
        slot = item.get("slot")
        item_id = item.get("id")
        count = item.get("count", 1)
        if slot is None or not item_id:
            continue
        entry = existing_by_slot.get(int(slot))
        if entry is None:
            entry = {
                "Slot": {"type": TAG_BYTE, "value": int(slot)},
                "id": {"type": TAG_STRING, "value": str(item_id)},
                "Count": {"type": TAG_BYTE, "value": int(count)},
            }
        else:
            entry["Slot"] = {"type": TAG_BYTE, "value": int(slot)}
            entry["id"] = {"type": TAG_STRING, "value": str(item_id)}
            entry["Count"] = {"type": TAG_BYTE, "value": int(count)}
        updated.append(entry)
    return updated


def _get_offline_inventory(instance_dir: Path, player: str) -> dict | None:
    playerdata = _resolve_playerdata(instance_dir, player)
    if not playerdata:
        return None
    root = read_nbt(str(playerdata))
    items = _extract_inventory_list(root)
    if not items:
        return {"items": [], "root": root, "path": playerdata}
    return {"items": items, "root": root, "path": playerdata}


def _set_offline_inventory(instance_dir: Path, player: str, desired: list[dict]) -> dict | None:
    payload = _get_offline_inventory(instance_dir, player)
    if not payload:
        return None
    root = payload["root"]
    compound = root.get("value", {})
    inv_tag = compound.get("Inventory")
    if not inv_tag:
        inv_tag = {"type": TAG_LIST, "value": {"item_type": TAG_COMPOUND, "items": []}}
        compound["Inventory"] = inv_tag
    inv_value = inv_tag["value"]
    if inv_value.get("item_type") != TAG_COMPOUND:
        inv_value["item_type"] = TAG_COMPOUND
        inv_value["items"] = []
    inv_value["items"] = _update_inventory_tags(inv_value.get("items", []), desired)
    root["value"] = compound
    write_nbt(str(payload["path"]), root)
    return {"applied": len(inv_value["items"])}


def _parse_inventory_payload(payload: str) -> list[dict]:
    items = []
    if not payload:
        return items
    if "No entity was found" in payload:
        return items
    for match in re.finditer(r"(?:Slot|slot):\s*(-?\d+)b?", payload, re.IGNORECASE):
        slot = int(match.group(1))
        window = payload[match.start() : match.start() + 240]
        id_match = re.search(r'id:\s*"?([a-z0-9_:\.\-]+)"?', window, re.IGNORECASE)
        count_match = re.search(r"(?:Count|count):\s*(\d+)", window, re.IGNORECASE)
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


def _resolve_online_player_name(client: RCONClient, player: str) -> str:
    try:
        names = client.list_players()
    except Exception:
        return player
    for name in names:
        if name.lower() == player.lower():
            return name
    return player


def _query_live_inventory(client: RCONClient, player: str, uuid: str | None = None) -> str:
    commands = [
        f"data get entity {player} Inventory",
        f"data get entity @a[name={player},limit=1] Inventory",
    ]
    if uuid:
        commands.append(f"data get entity @e[uuid={uuid},limit=1] Inventory")
    for command in commands:
        response = client.execute(command)
        if response.startswith("RCON ") or "No entity was found" in response:
            continue
        return response
    return "No entity was found"


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
    online_names = client.list_players()
    is_online = any(name.lower() == player.lower() for name in online_names)
    player_name = _resolve_online_player_name(client, player)
    uuid = _resolve_player_uuid(instance_path, player_name)
    response = _query_live_inventory(client, player_name, uuid)
    if response.startswith("RCON "):
        return {
            "supported": False,
            "provider": provider or "vanilla_rcon",
            "editable": False,
            "items": [],
            "message": response,
            "raw": response,
        }
    if "No entity was found" in response:
        if is_online:
            return {
                "supported": True,
                "provider": provider or "vanilla_rcon",
                "editable": True,
                "items": [],
                "message": "Inventory fetch failed for online player.",
                "raw": response,
            }
        offline = _get_offline_inventory(instance_path, player)
        if offline is not None:
            items = _inventory_items_from_tags(offline["items"])
            return {
                "supported": True,
                "provider": provider or "offline",
                "editable": True,
                "items": items,
                "message": None if items else "Offline inventory loaded.",
                "raw": response,
            }
        message = "Player is offline or not found. Join once to create player data."
        return {
            "supported": False,
            "provider": provider or "vanilla_rcon",
            "editable": False,
            "items": [],
            "message": message,
            "raw": response,
        }
    items = _parse_inventory_payload(response)
    if not items:
        raw_snippet = response[:1200] if response else None
        return {
            "supported": True,
            "provider": provider or "vanilla_rcon",
            "editable": True,
            "items": [],
            "message": "Inventory is empty." if raw_snippet is None else "Inventory parse failed.",
            "raw": raw_snippet,
        }
    return {
        "supported": True,
        "provider": provider or "vanilla_rcon",
        "editable": True,
        "items": items,
        "message": None,
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
    if player not in client.list_players() and provider:
        offline = _set_offline_inventory(instance_path, player, items)
        if offline is not None:
            return {
                "supported": True,
                "provider": provider,
                "editable": True,
                "message": f"Offline inventory updated ({offline['applied']} items).",
            }
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
