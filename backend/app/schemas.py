from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models import RoomMode, SessionStatus


class UserBase(BaseModel):
    display_name: str = Field(max_length=64)
    avatar_url: Optional[str] = Field(default=None, max_length=255)


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RoomCreate(BaseModel):
    name: str = Field(max_length=80)
    mode: RoomMode
    owner_id: UUID
    capacity: int = Field(default=4, ge=2, le=6)


class RoomSummary(BaseModel):
    id: UUID
    name: str
    mode: RoomMode
    player_count: int
    capacity: int
    is_open: bool
    created_at: datetime


class RoomMemberRead(BaseModel):
    user_id: UUID
    display_name: str
    alias: str
    joined_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RoomRead(BaseModel):
    id: UUID
    name: str
    mode: RoomMode
    owner_id: UUID
    capacity: int
    is_open: bool
    created_at: datetime
    members: list[RoomMemberRead]
    model_config = ConfigDict(from_attributes=True)


class JoinRoomRequest(BaseModel):
    user_id: UUID


class GameSessionCreate(BaseModel):
    mode: Optional[RoomMode] = None


class GameSessionRead(BaseModel):
    id: UUID
    room_id: UUID
    mode: RoomMode
    status: SessionStatus
    started_at: datetime
    ended_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class TurnLogCreate(BaseModel):
    actor_id: UUID
    payload: dict


class TurnLogRead(BaseModel):
    id: UUID
    session_id: UUID
    turn_number: int
    actor_id: UUID
    payload: dict
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
