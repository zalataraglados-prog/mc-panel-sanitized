"""
Modpack compatibility matrix (minimal v1).

Keys are modpack loader identifiers declared by users in claims params.
Values are the compatible stack.type values.
"""

MODPACK_STACK_COMPAT = {
    "vanilla": {"vanilla", "paper"},
    "paper": {"paper"},
    "fabric": {"fabric"},
    "forge": {"forge"},
    "neoforge": {"neoforge"},
}


def normalize_loader(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    return value.strip().lower()

