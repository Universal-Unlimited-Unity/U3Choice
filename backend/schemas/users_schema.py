from pydantic import BaseModel, Field, EmailStr
from datetime import date
from uuid import uuid4, UUID
class user(BaseModel):
    id: UUID = Field(default_factory=uuid4())
    username: str
    email: EmailStr
    pwd_hash: str
    name: str
    bio: str | None = Field(max_length=50)
    photo_url: str
    dob: date
    status: str
    created_at: date
    updated_at: date
    last_login: date
    verified: bool = False
    country: str = Field(max_length=2)

