from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.realtime.connection_manager import manager

router = APIRouter()


@router.websocket("/ws/dispatch/{tenant_id}")
async def dispatch_ws(websocket: WebSocket, tenant_id: str):
    await manager.connect(tenant_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(tenant_id, websocket)