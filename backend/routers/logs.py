from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status

from backend.auth import get_current_user
from backend.runtime.logs import stream_logs

router = APIRouter()


@router.websocket("/api/logs/ws")
async def logs_websocket(websocket: WebSocket, token: str):
    await websocket.accept()
    user = None
    try:
        user = get_current_user(f"Bearer {token}")
    except Exception as exc:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        await stream_logs(websocket, "/opt/mc-instances/latest/logs/latest.log")
    except WebSocketDisconnect:
        return
