import re

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")
_MC_COLOR_CODE = re.compile(r"§.")


def strip_ansi(text: str) -> str:
    if not text:
        return text
    text = _ANSI_ESCAPE.sub("", text)
    return _MC_COLOR_CODE.sub("", text)
