import pathlib


def tail_log(path: str, lines: int = 200):
    file_path = pathlib.Path(path)
    if not file_path.exists():
        return []
    with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
        return handle.readlines()[-lines:]
