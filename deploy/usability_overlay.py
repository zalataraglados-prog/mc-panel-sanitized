from __future__ import annotations

from typing import Any, Dict


def get_usability_entry(overlay: Dict[str, Any], section: str, key: str) -> Dict[str, Any] | None:
    if not isinstance(overlay, dict):
        return None
    section_data = overlay.get(section, {})
    entries = section_data.get("entries", {})
    value = entries.get(key)
    if isinstance(value, dict):
        return value
    return None
