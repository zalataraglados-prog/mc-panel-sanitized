import base64
import json

CLAIMS_SCHEMA_VERSION = 1


def encode_claims(params: dict) -> str:
    """
    Encode claims params as base64url(JSON).
    """

    if not isinstance(params, dict):
        raise ValueError("Invalid params payload")

    payload = {
        "v": CLAIMS_SCHEMA_VERSION,
        "params": params,
    }

    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    token = base64.urlsafe_b64encode(raw).decode("ascii")
    return token.rstrip("=")
