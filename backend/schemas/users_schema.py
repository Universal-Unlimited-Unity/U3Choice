from pydantic import BaseModel, Field, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import datetime, date, timezone
from uuid import uuid4, UUID
from enum import Enum

class Gender(str, Enum):
    Male = 'male'
    Female = 'female'

class Status(str, Enum):
    Active = 'Active'
    Suspended = 'Suspended'

class UserSummary(BaseModel):
    id: UUID
    username: str
    name: str
    photo_url: str
    country: str = Field(max_length=2)
    
    
class User_Profile(BaseModel):
    id: UUID
    username: str
    name: str
    bio: str | None = Field(max_length=50)
    photo_url: str = "assets/default_profile.png"
    country: str = Field(max_length=2)
    verified: bool = False
    status: Status
    
class Profile_View(BaseModel):
    viwed_id: str
    username: str
    viwer_id: str
    name: str
    bio: str | None = Field(max_length=50)
    photo_url: str = "assets/default_profile.png"
    country: str = Field(max_length=2)
    verified: bool = False
    status: Status
    is_owner: bool = False
    is_friends: bool = False
    is_blocked: bool = False
    has_sent_friendship_request: bool = False
    has_received_friendship_request: bool = False
    
class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    pwd_hash: str
    username: str
    email: EmailStr
    phone: PhoneNumber
    name: str
    bio: str | None = Field(max_length=50, default=None)
    photo_url: str = "assets/default_profile.png"
    dob: date
    status: Status = Status.Active
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None
    last_login: datetime | None = None
    verified: bool = False
    country: str = Field(max_length=2)
    email_verified: bool = False
    gender: Gender

class User_Update(BaseModel):
    username: str | None = None
    name: str | None = None
    bio: str | None = Field(max_length=50, default=None)
    photo_url: str | None = None
    country: str | None = Field(max_length=2, default=None)
    gender: Gender | None = None
    dob: date | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class Request_ID(BaseModel):
    id: UUID
