from collections import defaultdict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, tenant_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[tenant_id].append(websocket)

    def disconnect(self, tenant_id: str, websocket: WebSocket) -> None:
        if tenant_id in self.active_connections and websocket in self.active_connections[tenant_id]:
            self.active_connections[tenant_id].remove(websocket)

        if tenant_id in self.active_connections and not self.active_connections[tenant_id]:
            del self.active_connections[tenant_id]

    async def broadcast_to_tenant(self, tenant_id: str, message: dict) -> None:
        if tenant_id not in self.active_connections:
            return

        dead_connections: list[WebSocket] = []

        for connection in self.active_connections[tenant_id]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(tenant_id, connection)


manager = ConnectionManager()