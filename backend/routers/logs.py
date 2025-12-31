from pathlib import Path

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status

from backend.auth import get_current_user
from backend.runtime.log_streamer import tail_log

router = APIRouter()


@router.websocket("/api/logs/ws")
async def logs_websocket(websocket: WebSocket, token: str, instance_dir: str = "/opt/mc-instances"):
    await websocket.accept()
    try:
        user = get_current_user(f"Bearer {token}")
    except Exception as exc:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    log_path = Path(instance_dir) / "logs" / "latest.log"
    if not log_path.exists():
        await websocket.send_text("logs not found")
        await websocket.close()
        return
    try:
        lines = tail_log(str(log_path), lines=200)
        for line in lines:
            await websocket.send_text(line.strip())
        while True:
            await websocket.send_text("heartbeat")
            await websocket.receive_text()
    except WebSocketDisconnect:
        return
