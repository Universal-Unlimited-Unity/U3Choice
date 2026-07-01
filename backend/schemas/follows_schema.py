from pydantic import BaseModel
from uuid import UUID
from datetime import date

class follows(BaseModel):
    follower_id: UUID
    followed_id: UUID
    created_at: date

class follow_counts(BaseModel):
    user_id: UUID
    followers_count: int = 0
    following_count: int = 0