import re

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from backend.auth import get_current_user, require_roles
from backend.runtime.ansi import strip_ansi
from backend.runtime.log_paths import resolve_latest_log
from backend.runtime.log_streamer import follow_log, tail_log
from backend.routers.instances import resolve_instance_dir

router = APIRouter()
_TIME_PREFIX = re.compile(r"^\[\d{2}:\d{2}:\d{2}\]\s*")


def _strip_time_prefix(line: str) -> str:
    return strip_ansi(_TIME_PREFIX.sub("", line))


@router.websocket("/api/logs/ws")
async def logs_websocket(
    websocket: WebSocket,
    token: str,
    instance_dir: str | None = None,
    max_lines: int = 200,
    max_per_second: int = 50,
):
    await websocket.accept()
    try:
        user = get_current_user(f"Bearer {token}")
        require_roles(user, ["owner", "admin", "mod", "viewer"])
    except Exception as exc:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    target_dir = instance_dir or resolve_instance_dir()
    log_path = resolve_latest_log(target_dir)
    if not log_path.exists():
        await websocket.send_text("logs not found")
        await websocket.close()
        return
    max_lines = max(50, min(500, max_lines))
    max_per_second = max(10, min(200, max_per_second))
    try:
        lines = tail_log(log_path, lines=max_lines)
        for line in lines:
            await websocket.send_text(_strip_time_prefix(line.strip()))
        async for line in follow_log(log_path, max_lines=max_lines, max_per_second=max_per_second):
            await websocket.send_text(_strip_time_prefix(line))
    except WebSocketDisconnect:
        return
