from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GameRoom, GameSession, RoomMember, SessionStatus, TurnLog


async def get_or_create_active_session(db: AsyncSession, room: GameRoom) -> GameSession:
    statement = select(GameSession).where(
        GameSession.room_id == room.id,
        GameSession.status == SessionStatus.ACTIVE,
    )
    result = await db.execute(statement)
    session = result.scalar_one_or_none()
    if session:
        return session

    # Snapshot current members for history
    member_stmt = select(RoomMember).where(RoomMember.room_id == room.id).order_by(RoomMember.joined_at)
    members = (await db.execute(member_stmt)).scalars().all()
    snapshot = {
        "players": [
            {
                "user_id": str(member.user_id),
                "alias": member.alias,
                "joined_at": member.joined_at.isoformat(),
            }
            for member in members
        ]
    }

    session = GameSession(room_id=room.id, mode=room.mode, status=SessionStatus.ACTIVE, players_snapshot=snapshot)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def complete_session(db: AsyncSession, session: GameSession, status: SessionStatus) -> GameSession:
    session.status = status
    session.ended_at = session.ended_at or session.updated_at
    await db.commit()
    await db.refresh(session)
    return session


async def append_turn(
    db: AsyncSession,
    session_id: UUID,
    actor_id: UUID,
    payload: dict,
) -> TurnLog:
    max_stmt = select(func.max(TurnLog.turn_number)).where(TurnLog.session_id == session_id)
    max_value = (await db.execute(max_stmt)).scalar()
    turn_number = (max_value or 0) + 1

    turn = TurnLog(
        session_id=session_id,
        turn_number=turn_number,
        actor_id=actor_id,
        payload=payload,
    )
    db.add(turn)
    await db.commit()
    await db.refresh(turn)
    return turn


async def get_recent_turns(db: AsyncSession, session_id: UUID, limit: int = 25) -> list[TurnLog]:
    stmt = (
        select(TurnLog)
        .where(TurnLog.session_id == session_id)
        .order_by(TurnLog.turn_number.desc())
        .limit(limit)
    )
    return list(reversed((await db.execute(stmt)).scalars().all()))
