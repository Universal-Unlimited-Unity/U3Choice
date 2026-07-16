from pydantic import BaseModel, EmailStr

class credentials(BaseModel):
    email: EmailStr
    pwd: str