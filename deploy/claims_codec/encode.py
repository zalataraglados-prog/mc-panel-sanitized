import base64
import hashlib
import json

CLAIMS_SCHEMA_VERSION = 3


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _checksum(payload: dict) -> str:
    raw = _canonical_json(payload)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def encode_claims(params: dict) -> str:
    """
    Encode claims params as base64url(JSON).
    """

    if not isinstance(params, dict):
        raise ValueError("Invalid params payload")

    base_payload = {"v": CLAIMS_SCHEMA_VERSION, "params": params}
    canonical = _canonical_json(base_payload)
    payload = dict(base_payload)
    payload["len"] = len(canonical)
    payload["checksum"] = _checksum(base_payload)

    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    token = base64.urlsafe_b64encode(raw).decode("ascii")
    return token.rstrip("=")
