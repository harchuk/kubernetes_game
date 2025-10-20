from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, UniqueConstraint, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


class RoomMode(str, Enum):
    CLASSIC = "classic"
    JUNIOR = "junior"


class SessionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class User(TimestampMixin, SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    display_name: str = Field(index=True, max_length=64)
    avatar_url: Optional[str] = Field(default=None, max_length=255)

    rooms: List["RoomMember"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete"})


class GameRoom(TimestampMixin, SQLModel, table=True):
    __tablename__ = "rooms"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=80)
    mode: RoomMode = Field(sa_column_kwargs={"nullable": False})
    owner_id: UUID = Field(nullable=False, foreign_key="users.id")
    capacity: int = Field(default=4, ge=2, le=6)
    is_open: bool = Field(default=True)

    owner: Optional[User] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})
    members: List["RoomMember"] = Relationship(back_populates="room", sa_relationship_kwargs={"cascade": "all, delete"})
    sessions: List["GameSession"] = Relationship(back_populates="room")


class RoomMember(SQLModel, table=True):
    __tablename__ = "room_members"
    __table_args__ = (
        UniqueConstraint("user_id", "room_id", name="uq_member"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    room_id: UUID = Field(foreign_key="rooms.id", nullable=False)
    alias: str = Field(default="Player", max_length=32)
    joined_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: Optional[User] = Relationship(back_populates="rooms")
    room: Optional[GameRoom] = Relationship(back_populates="members")


class GameSession(TimestampMixin, SQLModel, table=True):
    __tablename__ = "sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    room_id: UUID = Field(foreign_key="rooms.id", nullable=False)
    mode: RoomMode = Field(sa_column_kwargs={"nullable": False})
    status: SessionStatus = Field(default=SessionStatus.PENDING)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    players_snapshot: dict = Field(sa_column=Column(JSONB), default_factory=dict)

    room: Optional[GameRoom] = Relationship(back_populates="sessions")
    turns: List["TurnLog"] = Relationship(back_populates="session")


class TurnLog(SQLModel, table=True):
    __tablename__ = "turn_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="sessions.id", nullable=False)
    turn_number: int = Field(nullable=False, ge=0)
    actor_id: UUID = Field(foreign_key="users.id", nullable=False)
    payload: dict = Field(sa_column=Column(JSONB), default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    session: Optional[GameSession] = Relationship(back_populates="turns")


def _set_updated_at(mapper, connection, target) -> None:  # type: ignore[no-untyped-def]
    if isinstance(target, TimestampMixin):
        target.updated_at = datetime.utcnow()


for model in (User, GameRoom, GameSession):
    event.listen(model, "before_update", _set_updated_at)
