from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from backend.auth import get_current_user, require_roles
from backend.runtime.log_streamer import follow_log, tail_log
from backend.routers.instances import resolve_instance_dir

router = APIRouter()


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
    log_path = Path(target_dir) / "logs" / "latest.log"
    if not log_path.exists():
        await websocket.send_text("logs not found")
        await websocket.close()
        return
    max_lines = max(50, min(500, max_lines))
    max_per_second = max(10, min(200, max_per_second))
    try:
        lines = tail_log(str(log_path), lines=max_lines)
        for line in lines:
            await websocket.send_text(line.strip())
        async for line in follow_log(str(log_path), max_lines=max_lines, max_per_second=max_per_second):
            await websocket.send_text(line)
    except WebSocketDisconnect:
        return
