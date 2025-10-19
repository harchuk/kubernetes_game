from __future__ import annotations

from collections import defaultdict
from typing import Dict, Set
from uuid import UUID

from fastapi import WebSocket


class RoomConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[UUID, Set[WebSocket]] = defaultdict(set)

    async def connect(self, room_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[room_id].add(websocket)

    def disconnect(self, room_id: UUID, websocket: WebSocket) -> None:
        connections = self.active_connections.get(room_id)
        if connections and websocket in connections:
            connections.remove(websocket)
            if not connections:
                self.active_connections.pop(room_id, None)

    async def broadcast(self, room_id: UUID, message: dict) -> None:
        for connection in list(self.active_connections.get(room_id, [])):
            await connection.send_json(message)


manager = RoomConnectionManager()
