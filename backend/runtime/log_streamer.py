import asyncio
import pathlib
import time
from typing import AsyncIterator, List


def tail_log(path: str, lines: int = 200) -> List[str]:
    file_path = pathlib.Path(path)
    if not file_path.exists():
        return []
    with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
        return handle.readlines()[-lines:]


async def follow_log(
    path: str, *, poll_interval: float = 0.5, flush_interval: float = 1.0, max_lines: int = 200
) -> AsyncIterator[str]:
    file_path = pathlib.Path(path)
    if not file_path.exists():
        return
    with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
        handle.seek(0, 2)
        buffer: List[str] = []
        last_flush = time.monotonic()
        while True:
            line = handle.readline()
            if not line:
                now = time.monotonic()
                if buffer and now - last_flush >= flush_interval:
                    yield "\n".join(buffer)
                    buffer.clear()
                    last_flush = now
                await asyncio.sleep(poll_interval)
                continue
            buffer.append(line.rstrip("\n"))
            now = time.monotonic()
            if len(buffer) >= max_lines or now - last_flush >= flush_interval:
                yield "\n".join(buffer)
                buffer.clear()
                last_flush = now
            else:
                yield buffer.pop()
