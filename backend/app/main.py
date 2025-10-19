from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.db.session import async_session_factory, init_db
from app.models import GameRoom
from app.services.gameplay import append_turn, get_or_create_active_session, get_recent_turns
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

    async with async_session_factory() as db:
        room = await db.get(GameRoom, room_id)
        if not room:
            await websocket.send_json({"type": "error", "detail": "room_not_found"})
            await websocket.close(code=1008)
            manager.disconnect(room_id, websocket)
            return
        game_session = await get_or_create_active_session(db, room)
        history = await get_recent_turns(db, game_session.id)

    await websocket.send_json(
        {
            "type": "session_snapshot",
            "session_id": str(game_session.id),
            "mode": game_session.mode,
            "players": game_session.players_snapshot.get("players", []),
        }
    )
    for entry in history:
        await websocket.send_json(
            {
                "type": "turn",
                "turn_id": str(entry.id),
                "turn_number": entry.turn_number,
                "actor_id": str(entry.actor_id),
                "created_at": entry.created_at.isoformat(),
                "payload": entry.payload,
            }
        )

    await manager.broadcast(
        room_id,
        {"type": "system", "message": "user_joined", "user_id": str(user_id) if user_id else None},
    )
    try:
        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")
            broadcast_payload = {
                "type": msg_type or "event",
                "user_id": str(user_id) if user_id else None,
                "payload": message.get("payload", message),
            }
            if msg_type == "turn" and user_id:
                async with async_session_factory() as db:
                    turn = await append_turn(
                        db,
                        session_id=game_session.id,
                        actor_id=user_id,
                        payload=message.get("payload", {}),
                    )
                broadcast_payload = {
                    "type": "turn",
                    "turn_id": str(turn.id),
                    "turn_number": turn.turn_number,
                    "actor_id": str(turn.actor_id),
                    "created_at": turn.created_at.isoformat(),
                    "payload": turn.payload,
                }
            await manager.broadcast(room_id, broadcast_payload)
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
        await manager.broadcast(
            room_id,
            {"type": "system", "message": "user_left", "user_id": str(user_id) if user_id else None},
        )
