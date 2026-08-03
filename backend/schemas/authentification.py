from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
class credentials(BaseModel):
    email: EmailStr
    pwd: str
    last_login: datetime = Field(default_factory= lambda: datetime.now(timezone.utc))