import base64
import json
from typing import Any, Dict

CLAIMS_SCHEMA_VERSION = 2


class Claims:
    """
    Minimal CapabilityClaims implementation for codec consumers.
    """

    def __init__(self, *, params: Dict[str, Any], profile: str):
        self.params = params
        self.profile = profile

    def param_capability(self, param_key: str) -> str:
        return param_key.split(".", 1)[0]


def _add_padding(s: str) -> str:
    missing = len(s) % 4
    if missing:
        return s + ("=" * (4 - missing))
    return s


def decode_claims(s: str) -> Claims:
    """
    Decode base64url(JSON) into Claims (v1/v2).
    """

    try:
        raw = base64.urlsafe_b64decode(_add_padding(s)).decode("utf-8")
        data = json.loads(raw)
    except Exception as exc:
        raise ValueError("Invalid claims string") from exc

    if not isinstance(data, dict):
        raise ValueError("Invalid claims payload")

    version = data.get("v")
    if version not in (1, CLAIMS_SCHEMA_VERSION):
        raise ValueError("Unsupported claims version")

    profile = data.get("profile")
    params = data.get("params")

    if not isinstance(profile, str):
        raise ValueError("Invalid profile in claims")
    if params is None:
        params = {}
    if not isinstance(params, dict):
        raise ValueError("Invalid params in claims")

    return Claims(profile=profile, params=params)
