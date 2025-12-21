import base64
import json

CLAIMS_SCHEMA_VERSION = 2


def encode_claims(claims) -> str:
    """
    Encode Claims as base64url(JSON).
    """

    if hasattr(claims, "profile") and hasattr(claims, "params"):
        profile = claims.profile
        params = claims.params
    elif isinstance(claims, dict):
        profile = claims.get("profile")
        params = claims.get("params")
    else:
        raise ValueError("Invalid claims object")

    params = params or {}
    payload = {
        "v": CLAIMS_SCHEMA_VERSION,
        "profile": profile,
        "params": params,
    }

    if "edition" in params:
        payload["edition"] = params["edition"]
    if "stack.type" in params:
        payload["stack.type"] = params["stack.type"]
    if "runtime.java" in params:
        payload["runtime.java"] = params["runtime.java"]

    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    token = base64.urlsafe_b64encode(raw).decode("ascii")
    return token.rstrip("=")
