from pydantic import BaseModel, Field, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import datetime, date, timezone
from uuid import uuid4, UUID
from enum import Enum

class Status(str, Enum):
    Active = 'Active'
    Suspended = 'Suspended'

class User_Profile(BaseModel):
    id: UUID
    username: str
    name: str
    bio: str | None = Field(max_length=50)
    photo_url: str
    country: str = Field(max_length=2)
    verified: bool = False
    status: Status
    
class Profile_View(BaseModel):
    viwed_id: UUID
    username: str
    viwer_id: UUID
    name: str
    bio: str | None = Field(max_length=50)
    photo_url: str
    country: str = Field(max_length=2)
    verified: bool = False
    status: Status
    is_owner: bool = False
    
class User(BaseModel):
    id: UUID = Field(default_factory=uuid4())
    pwd_hash: str
    username: str
    email: EmailStr
    phone: PhoneNumber
    name: str
    bio: str | None = Field(max_length=50)
    photo_url: str
    dob: date
    status: Status = Status.Active
    created_at: datetime = Field(default_factory=datetime.now())
    updated_at: datetime | None = None
    last_login: datetime | None = None
    verified: bool = False
    country: str = Field(max_length=2)
    email_verified: bool = False
    
class Request_ID(BaseModel):
    id: UUID
