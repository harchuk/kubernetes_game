from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import GameRoom, GameSession, RoomMember, RoomMode, SessionStatus, TurnLog, User
from app.schemas import (
    GameSessionCreate,
    GameSessionRead,
    JoinRoomRequest,
    RoomCreate,
    RoomMemberRead,
    RoomRead,
    RoomSummary,
    TurnLogCreate,
    TurnLogRead,
)
from app.services.gameplay import append_turn, get_or_create_active_session, get_recent_turns

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/", response_model=list[RoomSummary])
async def list_rooms(
    mode: RoomMode | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[RoomSummary]:
    stmt = select(
        GameRoom,
        func.count(RoomMember.id).label("player_count"),
    ).join(RoomMember, RoomMember.room_id == GameRoom.id, isouter=True)

    if mode:
        stmt = stmt.where(GameRoom.mode == mode)

    stmt = stmt.group_by(GameRoom.id).order_by(GameRoom.created_at.desc())
    result = await session.execute(stmt)

    summaries: list[RoomSummary] = []
    for room, player_count in result.all():
        summaries.append(
            RoomSummary(
                id=room.id,
                name=room.name,
                mode=room.mode,
                player_count=int(player_count or 0),
                capacity=room.capacity,
                is_open=room.is_open,
                created_at=room.created_at,
            )
        )
    return summaries


@router.post("/", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(payload: RoomCreate, session: AsyncSession = Depends(get_session)) -> RoomRead:
    owner = await session.get(User, payload.owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    room = GameRoom(
        name=payload.name,
        mode=payload.mode,
        owner_id=payload.owner_id,
        capacity=payload.capacity,
    )
    session.add(room)
    await session.flush()

    membership = RoomMember(user_id=payload.owner_id, room_id=room.id, alias="Player 1")
    session.add(membership)
    await session.commit()
    await session.refresh(room)

    return await _room_to_schema(room, session)


@router.get("/{room_id}", response_model=RoomRead)
async def get_room(room_id: UUID, session: AsyncSession = Depends(get_session)) -> RoomRead:
    room = await session.get(GameRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return await _room_to_schema(room, session)


@router.post("/{room_id}/join", response_model=RoomRead)
async def join_room(
    room_id: UUID,
    payload: JoinRoomRequest,
    session: AsyncSession = Depends(get_session),
) -> RoomRead:
    room = await session.get(GameRoom, room_id)
    if not room or not room.is_open:
        raise HTTPException(status_code=404, detail="Room not available")

    user = await session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    count_stmt = select(func.count(RoomMember.id)).where(RoomMember.room_id == room_id)
    player_count = (await session.execute(count_stmt)).scalar_one()
    if player_count >= room.capacity:
        raise HTTPException(status_code=409, detail="Room is full")

    existing_stmt = select(RoomMember).where(RoomMember.room_id == room_id, RoomMember.user_id == payload.user_id)
    existing = (await session.execute(existing_stmt)).scalar_one_or_none()
    if not existing:
        alias_stmt = select(RoomMember.alias).where(RoomMember.room_id == room_id)
        aliases = [row[0] for row in (await session.execute(alias_stmt)).all()]
        next_number = 1
        for alias in aliases:
            if alias.startswith("Player "):
                try:
                    number = int(alias.split(" ")[1])
                    next_number = max(next_number, number + 1)
                except (IndexError, ValueError):
                    continue
        session.add(RoomMember(user_id=payload.user_id, room_id=room_id, alias=f"Player {next_number}"))
    await session.commit()

    refreshed = await session.get(GameRoom, room_id)
    return await _room_to_schema(refreshed, session)


@router.post("/{room_id}/sessions", response_model=GameSessionRead, status_code=status.HTTP_201_CREATED)
async def start_session(
    room_id: UUID,
    payload: GameSessionCreate,
    session: AsyncSession = Depends(get_session),
) -> GameSessionRead:
    room = await session.get(GameRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    mode = payload.mode or room.mode

    active_stmt = select(GameSession).where(
        GameSession.room_id == room_id, GameSession.status == SessionStatus.ACTIVE
    )
    active = (await session.execute(active_stmt)).scalar_one_or_none()
    if active:
        raise HTTPException(status_code=409, detail="Session already active")

    member_stmt = select(RoomMember).where(RoomMember.room_id == room_id).order_by(RoomMember.joined_at)
    members = (await session.execute(member_stmt)).scalars().all()
    snapshot = {
        "players": [
            {
                "user_id": str(member.user_id),
                "alias": member.alias,
                "joined_at": member.joined_at.isoformat(),
            }
            for member in members
        ],
    }

    game_session = GameSession(
        room_id=room_id,
        mode=mode,
        status=SessionStatus.ACTIVE,
        players_snapshot=snapshot,
    )
    session.add(game_session)
    await session.commit()
    await session.refresh(game_session)
    return GameSessionRead.model_validate(game_session)


@router.get("/{room_id}/sessions/{session_id}", response_model=GameSessionRead)
async def get_session(room_id: UUID, session_id: UUID, db: AsyncSession = Depends(get_session)) -> GameSessionRead:
    statement = select(GameSession).where(GameSession.id == session_id, GameSession.room_id == room_id)
    result = await db.execute(statement)
    game_session = result.scalar_one_or_none()
    if not game_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return GameSessionRead.model_validate(game_session)


@router.post("/{room_id}/sessions/{session_id}/turns", response_model=TurnLogRead, status_code=status.HTTP_201_CREATED)
async def add_turn(
    room_id: UUID,
    session_id: UUID,
    payload: TurnLogCreate,
    db: AsyncSession = Depends(get_session),
) -> TurnLogRead:
    session_exists = await db.get(GameSession, session_id)
    if not session_exists or session_exists.room_id != room_id:
        raise HTTPException(status_code=404, detail="Session not found")

    turn = await append_turn(db, session_id=session_id, actor_id=payload.actor_id, payload=payload.payload)
    return TurnLogRead.model_validate(turn)


@router.post("/{room_id}/sessions/{session_id}/complete", response_model=GameSessionRead)
async def complete_session_endpoint(
    room_id: UUID,
    session_id: UUID,
    db: AsyncSession = Depends(get_session),
) -> GameSessionRead:
    statement = select(GameSession).where(GameSession.id == session_id, GameSession.room_id == room_id)
    result = await db.execute(statement)
    game_session = result.scalar_one_or_none()
    if not game_session:
        raise HTTPException(status_code=404, detail="Session not found")
    game_session.status = SessionStatus.COMPLETED
    game_session.ended_at = datetime.utcnow()
    await db.commit()
    await db.refresh(game_session)
    return GameSessionRead.model_validate(game_session)


async def _room_to_schema(room: GameRoom, session: AsyncSession) -> RoomRead:
    join_stmt = (
        select(RoomMember, User.display_name)
        .join(User, RoomMember.user_id == User.id)
        .where(RoomMember.room_id == room.id)
        .order_by(RoomMember.joined_at)
    )
    result = await session.execute(join_stmt)
    members = [
        RoomMemberRead(
            user_id=member.user_id,
            display_name=display_name,
            alias=member.alias,
            joined_at=member.joined_at,
        )
        for member, display_name in result.all()
    ]

    return RoomRead(
        id=room.id,
        name=room.name,
        mode=room.mode,
        owner_id=room.owner_id,
        capacity=room.capacity,
        is_open=room.is_open,
        created_at=room.created_at,
        members=members,
    )
