import base64
import json


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

    payload = {
        "v": 1,
        "profile": profile,
        "params": params or {},
    }

    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    token = base64.urlsafe_b64encode(raw).decode("ascii")
    return token.rstrip("=")
