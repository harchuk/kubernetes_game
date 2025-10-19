from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.db.session import init_db
from app.services.room_ws import manager

app = FastAPI(title=settings.app_name)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws/rooms/{room_id}")
async def websocket_room_endpoint(
    websocket: WebSocket,
    room_id: UUID,
    user_id: UUID | None = Query(default=None),
) -> None:
    await manager.connect(room_id, websocket)
    await manager.broadcast(
        room_id,
        {"type": "system", "message": "user_joined", "user_id": str(user_id) if user_id else None},
    )
    try:
        while True:
            message = await websocket.receive_json()
            await manager.broadcast(
                room_id,
                {
                    "type": "event",
                    "user_id": str(user_id) if user_id else None,
                    "payload": message,
                },
            )
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
        await manager.broadcast(
            room_id,
            {"type": "system", "message": "user_left", "user_id": str(user_id) if user_id else None},
        )
