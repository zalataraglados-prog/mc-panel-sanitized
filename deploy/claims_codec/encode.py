import base64
import hashlib
import json

CLAIMS_SCHEMA_VERSION = 2


def _checksum(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def encode_claims(params: dict) -> str:
    """
    Encode claims params as base64url(JSON).
    """

    if not isinstance(params, dict):
        raise ValueError("Invalid params payload")

    base_payload = {
        "v": CLAIMS_SCHEMA_VERSION,
        "params": params,
    }
    payload = dict(base_payload)
    payload["checksum"] = _checksum(base_payload)

    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    token = base64.urlsafe_b64encode(raw).decode("ascii")
    return token.rstrip("=")
