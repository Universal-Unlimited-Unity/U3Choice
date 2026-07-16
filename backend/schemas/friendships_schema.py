from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, timezone
from enum import Enum

class Status(str, Enum):    
    Pending = 'Pending'
    Accepted = 'Accepted'

class Friendships(BaseModel):
    sender_id: UUID
    receiver_id: UUID
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime | None = None
    status: Status = Status.Pending


class blocked_friendships(BaseModel):
    blocker_id: UUID
    blocked_id: UUID
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))

class Friendships_short(BaseModel):
    sender_id: UUID
    receiver_id: UUID

class blocked_friendships_short(BaseModel):
    blocker_id: UUID
    blocked_id: UUID