import base64
import json
from urllib.parse import parse_qs, quote, unquote


PREFIX = "c1|"

# Compact metadata keys (short -> full).
_META_KEYS = {
    "e": "edition",
    "s": "stack.type",
    "r": "runtime.java",
    "m": "docker.env.MEMORY",
    "p": "deploy.expected_players",
}
_META_KEYS_REVERSE = {v: k for k, v in _META_KEYS.items()}


def is_compact_string(s: str) -> bool:
    return isinstance(s, str) and s.startswith(PREFIX)


def peek_version(s: str) -> str:
    if not is_compact_string(s):
        raise ValueError("Not a compact claims string")
    parts = s.split("|", 3)
    if len(parts) < 3 or not parts[1]:
        raise ValueError("Compact claims string missing version")
    return parts[1]


def _add_padding(s: str) -> str:
    missing = len(s) % 4
    if missing:
        return s + ("=" * (4 - missing))
    return s


def _build_key_list(catalog: dict) -> list[str]:
    if not isinstance(catalog, dict):
        raise ValueError("Invalid catalog")
    server_entries = catalog.get("server_properties", {}).get("entries", {})
    gamerule_entries = catalog.get("gamerule", {}).get("entries", {})
    if not isinstance(server_entries, dict) or not isinstance(gamerule_entries, dict):
        raise ValueError("Invalid catalog entries")
    return list(server_entries.keys()) + list(gamerule_entries.keys())


def _encode_value(value) -> str:
    return quote(str(value), safe="-_.~")


def encode_compact(params: dict, catalog: dict, version: str) -> str:
    if not isinstance(params, dict):
        raise ValueError("Invalid params payload")
    if not isinstance(version, str) or not version:
        raise ValueError("Invalid version for compact claims")

    key_list = _build_key_list(catalog)
    index_map = {key: idx for idx, key in enumerate(key_list)}

    pairs = []
    meta_pairs = []
    extras = {}

    for key, value in params.items():
        if key in index_map:
            idx = format(index_map[key], "x")
            pairs.append(f"{idx}={_encode_value(value)}")
            continue
        short = _META_KEYS_REVERSE.get(key)
        if short:
            meta_pairs.append(f"{short}={_encode_value(value)}")
            continue
        extras[key] = value

    meta = ""
    if extras:
        raw = json.dumps(extras, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        token = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
        meta_pairs.append(f"x={token}")
    if meta_pairs:
        meta = "&".join(meta_pairs)

    pair_segment = ",".join(pairs)
    if meta:
        return f"{PREFIX}{version}|{pair_segment}|{meta}"
    return f"{PREFIX}{version}|{pair_segment}"


def decode_compact(s: str, catalog: dict) -> dict:
    if not is_compact_string(s):
        raise ValueError("Not a compact claims string")

    parts = s.split("|", 3)
    if len(parts) < 3:
        raise ValueError("Invalid compact claims string")
    pair_segment = parts[2]
    meta_segment = parts[3] if len(parts) > 3 else ""

    key_list = _build_key_list(catalog)

    params = {}
    if pair_segment:
        for item in pair_segment.split(","):
            if not item:
                continue
            if "=" not in item:
                raise ValueError("Invalid compact pair")
            idx_str, value_str = item.split("=", 1)
            try:
                idx = int(idx_str, 16)
            except ValueError as exc:
                raise ValueError("Invalid compact index") from exc
            if idx < 0 or idx >= len(key_list):
                raise ValueError("Compact index out of range")
            key = key_list[idx]
            params[key] = unquote(value_str)

    if meta_segment:
        meta = parse_qs(meta_segment, keep_blank_values=True)
        for short, full in _META_KEYS.items():
            values = meta.get(short)
            if values:
                params[full] = unquote(values[0])
        extras_token = meta.get("x", [])
        if extras_token:
            raw = base64.urlsafe_b64decode(_add_padding(extras_token[0])).decode("utf-8")
            extras = json.loads(raw)
            if not isinstance(extras, dict):
                raise ValueError("Invalid compact extras")
            params.update(extras)

    return params
