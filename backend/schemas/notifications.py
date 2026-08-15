from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum

class Type(str, Enum):
    Accept = "Accept"
    Sent = "Sent"
    
    
class Notification(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    root_id: UUID
    concerned_id: UUID
    type: Type
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
