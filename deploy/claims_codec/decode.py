import base64
import hashlib
import json
from typing import Any, Dict

CLAIMS_SCHEMA_VERSION = 2


class Claims:
    """
    Minimal CapabilityClaims implementation for codec consumers.
    """

    def __init__(self, *, params: Dict[str, Any], profile: str, imported: bool = False):
        self.params = params
        self.profile = profile
        self.imported_from_string = imported

    def param_capability(self, param_key: str) -> str:
        return param_key.split(".", 1)[0]


def _add_padding(s: str) -> str:
    missing = len(s) % 4
    if missing:
        return s + ("=" * (4 - missing))
    return s


def decode_claims(s: str) -> dict:
    """
    Decode base64url(JSON) into params (v1).
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

    params = data.get("params")

    if params is None:
        raise ValueError("Invalid params in claims")
    if not isinstance(params, dict):
        raise ValueError("Invalid params in claims")

    if version == CLAIMS_SCHEMA_VERSION:
        checksum = data.get("checksum")
        if not isinstance(checksum, str):
            raise ValueError("Missing checksum in claims")
        base_payload = {"v": CLAIMS_SCHEMA_VERSION, "params": params}
        raw = json.dumps(base_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        expected = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        if checksum != expected:
            raise ValueError("Invalid checksum in claims")

    return params
