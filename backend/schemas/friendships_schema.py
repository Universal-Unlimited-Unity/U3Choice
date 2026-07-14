from pydantic import BaseModel
from uuid import UUID
from datetime import date

class Status(str, Enum):    
    Pending = 'Pending'
    Accepted = 'Accepted'
    Rejected = 'Rejected'

class Friendships(BaseModel):
    sender_id: UUID
    receiver_id: UUID
    created_at: date
    updated_at: date | None = None
    status: Status = Status.Pending


