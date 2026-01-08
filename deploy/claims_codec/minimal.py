import re
from urllib.parse import quote, unquote


PREFIX_VERSION = "v"
PREFIX_TEMPLATE = "tpl"
SECTION_SERVER = "s:"
SECTION_GAMERULE = "g:"
SECTION_EXTRA = "x:"


def is_minimal_string(s: str) -> bool:
    if not isinstance(s, str):
        return False
    text = s.strip()
    return text.startswith(PREFIX_VERSION) and SECTION_SERVER in text


def peek_version(s: str) -> str:
    if not is_minimal_string(s):
        raise ValueError("Not a minimal claims string")
    first = s.strip().split(";", 1)[0]
    if not first.startswith(PREFIX_VERSION):
        raise ValueError("Minimal claims string missing version")
    return first[len(PREFIX_VERSION) :].strip().lstrip()


def _encode_token(value: str) -> str:
    return quote(str(value), safe="-_.~")


def _decode_token(value: str) -> str:
    return unquote(value)


def _build_key_list(catalog: dict, section: str) -> list[str]:
    entries = catalog.get(section, {}).get("entries", {})
    if not isinstance(entries, dict):
        raise ValueError("Invalid catalog entries")
    return list(entries.keys())


def _defaults_from_catalog(catalog: dict) -> dict:
    params: dict = {}
    for section in ("server_properties", "gamerule"):
        entries = catalog.get(section, {}).get("entries", {})
        for key, meta in entries.items():
            if "default" in meta:
                params[key] = meta["default"]
    return params


def _coerce_value(value: str, default):
    if isinstance(default, bool):
        lowered = value.strip().lower()
        if lowered in ("true", "1", "yes", "y"):
            return True
        if lowered in ("false", "0", "no", "n"):
            return False
        return value
    if isinstance(default, int):
        try:
            return int(value)
        except ValueError:
            return value
    return value


def encode_minimal(params: dict, catalog: dict, version: str, template: str = "vanilla") -> str:
    if not isinstance(params, dict):
        raise ValueError("Invalid params payload")
    if not isinstance(catalog, dict):
        raise ValueError("Invalid catalog payload")
    if not isinstance(version, str) or not version:
        raise ValueError("Invalid version for minimal claims")

    full_params = _defaults_from_catalog(catalog)
    full_params.update(params)

    server_keys = _build_key_list(catalog, "server_properties")
    gamerule_keys = _build_key_list(catalog, "gamerule")

    server_pairs = []
    for key in server_keys:
        if key not in full_params:
            raise ValueError(f"Missing server property: {key}")
        server_pairs.append(f"{_encode_token(key)}:{_encode_token(full_params[key])}")

    gamerule_pairs = []
    for key in gamerule_keys:
        if key not in full_params:
            raise ValueError(f"Missing gamerule: {key}")
        gamerule_pairs.append(f"{_encode_token(key)}:{_encode_token(full_params[key])}")

    extras = {}
    for key, value in full_params.items():
        if key in server_keys or key in gamerule_keys:
            continue
        extras[key] = value

    parts = [f"{PREFIX_VERSION} {_encode_token(version)}", f"{PREFIX_TEMPLATE} {_encode_token(template)}"]
    parts.append(f"{SECTION_SERVER}{'|'.join(server_pairs)}")
    parts.append(f"{SECTION_GAMERULE}{'|'.join(gamerule_pairs)}")
    if extras:
        extra_pairs = [f"{_encode_token(k)}:{_encode_token(v)}" for k, v in sorted(extras.items())]
        parts.append(f"{SECTION_EXTRA}{'|'.join(extra_pairs)}")
    return ";".join(parts)


def decode_minimal(s: str, catalog: dict) -> dict:
    if not is_minimal_string(s):
        raise ValueError("Not a minimal claims string")
    if not isinstance(catalog, dict):
        raise ValueError("Invalid catalog payload")

    text = s.strip()
    segments = [seg.strip() for seg in text.split(";") if seg.strip()]
    params: dict = {}

    server_defaults = catalog.get("server_properties", {}).get("entries", {})
    gamerule_defaults = catalog.get("gamerule", {}).get("entries", {})

    for seg in segments:
        if seg.startswith(PREFIX_VERSION) or seg.startswith(PREFIX_TEMPLATE):
            continue
        if seg.startswith(SECTION_SERVER):
            payload = seg[len(SECTION_SERVER) :]
            if payload:
                for item in payload.split("|"):
                    if not item:
                        continue
                    if ":" not in item:
                        raise ValueError("Invalid minimal server entry")
                    raw_key, raw_value = item.split(":", 1)
                    key = _decode_token(raw_key)
                    value = _decode_token(raw_value)
                    meta = server_defaults.get(key, {})
                    params[key] = _coerce_value(value, meta.get("default"))
            continue
        if seg.startswith(SECTION_GAMERULE):
            payload = seg[len(SECTION_GAMERULE) :]
            if payload:
                for item in payload.split("|"):
                    if not item:
                        continue
                    if ":" not in item:
                        raise ValueError("Invalid minimal gamerule entry")
                    raw_key, raw_value = item.split(":", 1)
                    key = _decode_token(raw_key)
                    value = _decode_token(raw_value)
                    meta = gamerule_defaults.get(key, {})
                    params[key] = _coerce_value(value, meta.get("default"))
            continue
        if seg.startswith(SECTION_EXTRA):
            payload = seg[len(SECTION_EXTRA) :]
            if payload:
                for item in payload.split("|"):
                    if not item:
                        continue
                    if ":" not in item:
                        raise ValueError("Invalid minimal extra entry")
                    raw_key, raw_value = item.split(":", 1)
                    key = _decode_token(raw_key)
                    value = _decode_token(raw_value)
                    if re.fullmatch(r"-?\d+", value):
                        params[key] = int(value)
                    elif value.strip().lower() in ("true", "false"):
                        params[key] = value.strip().lower() == "true"
                    else:
                        params[key] = value
            continue
        raise ValueError("Invalid minimal claims segment")

    return params
