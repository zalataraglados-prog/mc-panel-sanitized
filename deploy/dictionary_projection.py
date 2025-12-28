from __future__ import annotations

from typing import Any, Dict, Set

from deploy.usability_overlay import get_usability_entry


def build_projections(
    *,
    catalog: Dict[str, Any],
    taxonomy: Dict[str, Any],
    usability: Dict[str, Any] | None = None,
) -> Dict[str, Set[str]]:
    usability = usability or {}
    server_entries = catalog.get("server_properties", {}).get("entries", {})
    gamerule_entries = catalog.get("gamerule", {}).get("entries", {})
    tax_server = taxonomy.get("server_properties", {}).get("entries", {})
    tax_gamerule = taxonomy.get("gamerule", {}).get("entries", {})

    novice_visible: Set[str] = set()
    advanced_visible: Set[str] = set()
    dangerous_visible: Set[str] = set()

    def _handle(section: str, key: str, tax: Dict[str, Any]):
        usability_entry = get_usability_entry(usability, section, key) or {}
        exposed = usability_entry.get("exposed", True)
        if exposed is False:
            return
        sensitivity = tax.get("sensitivity")
        risk = tax.get("risk")
        if sensitivity == "novice":
            novice_visible.add(key)
        if sensitivity == "advanced":
            advanced_visible.add(key)
        if risk == "high":
            dangerous_visible.add(key)

    for key in server_entries.keys():
        tax = tax_server.get(key, {})
        _handle("server_properties", key, tax)

    for key in gamerule_entries.keys():
        tax = tax_gamerule.get(key, {})
        _handle("gamerule", key, tax)

    return {
        "novice_visible": novice_visible,
        "advanced_visible": advanced_visible,
        "dangerous_visible": dangerous_visible,
    }
