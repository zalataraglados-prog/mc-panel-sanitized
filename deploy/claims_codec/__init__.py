from .encode import encode_claims
from .decode import decode_claims, Claims
from .compact import decode_compact, encode_compact, is_compact_string, peek_version
from .minimal import decode_minimal, encode_minimal, is_minimal_string, peek_version as peek_version_min


def decode_auto(s: str, catalog: dict | None = None) -> dict:
    if is_compact_string(s):
        if catalog is None:
            raise ValueError("Catalog required for compact claims")
        return decode_compact(s, catalog)
    if is_minimal_string(s):
        if catalog is None:
            raise ValueError("Catalog required for minimal claims")
        return decode_minimal(s, catalog)
    return decode_claims(s)

__all__ = [
    "Claims",
    "decode_claims",
    "decode_compact",
    "encode_claims",
    "encode_compact",
    "encode_minimal",
    "decode_minimal",
    "is_compact_string",
    "is_minimal_string",
    "peek_version",
    "peek_version_min",
    "decode_auto",
]
