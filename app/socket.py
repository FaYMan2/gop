from fastapi import websockets


class wsConnectionManager:
    def __init__(self):
        self.active_connections: set[websockets.WebSocket] = set()

    async def connect(self, websocket: websockets.WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
    def disconnect(self, websocket: websockets.WebSocket):
        self.active_connections.discard(websocket)

    async def send_personal_message(self, message: str, websocket: websockets.WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)
