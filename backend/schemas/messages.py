from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import UUID, uuid4
class Message(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    sender_id: UUID
    receiver_id: UUID
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



