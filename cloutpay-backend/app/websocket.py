from fastapi import WebSocket
from collections import deque


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.recent_activities: deque = deque(maxlen=10)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Push last 10 activities to the newly connected client
        if self.recent_activities:
            await websocket.send_json({
                "type": "INIT_ACTIVITIES",
                "payload": list(self.recent_activities)
            })

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Store activity events for new connections
        if message.get("type") == "NEW_ACTIVITY":
            self.recent_activities.appendleft(message["payload"])

        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for c in dead:
            self.disconnect(c)


manager = ConnectionManager()