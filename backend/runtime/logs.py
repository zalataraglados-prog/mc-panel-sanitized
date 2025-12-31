import asyncio
import os


async def stream_logs(websocket, log_path: str, *, limit: int = 100):
    if not os.path.exists(log_path):
        await websocket.send_text("logs not found")
        return
    with open(log_path, "r", encoding="utf-8", errors="ignore") as handle:
        lines = handle.readlines()[-limit:]
    for line in lines:
        await websocket.send_text(line.strip())
        await asyncio.sleep(0.1)
    while True:
        await asyncio.sleep(1)
        await websocket.send_text("heartbeat")
