from backend.database import eng
from sqlalchemy import select, insert
from backend.models import users_table
from password_validator import PasswordValidator
from schemas.users_schema import User
from passlib.context import CryptContext
from pydantic import EmailStr
from jose import jwt
from datetime import datetime, timedelta
from config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="VerifyToken")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        user = decode_token(token)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    
pwd_context = CryptContext(schemes=["bcrypt"], deprecated='auto')

def username_used(username: str):
    with eng.connect() as conn:
        stmt = select(users_table).where(users_table.c.id == username)
        result = conn.execute(stmt).fetchone()
        return result
    
def email_used(email: str):
    with eng.connect() as conn:
        stmt = select(users_table).where(users_table.c.email == email)
        result = conn.execute(stmt).fetchone()
        return result
    
def pwd_strong(pwd: str):
    schema = (PasswordValidator()
    .min(8)
    .has().uppercase()
    .has().lowercase()
    .has().digits()
    .has().symbols()
    )
    return schema.validate(pwd)

def signup(user: User):
    with eng.begin() as conn:
        dumped_user = user.model_dump()
        conn.execute(insert(users_table).values(dumped_user))

def hash_pwd(pwd_plain: str):
    return pwd_context.hash(pwd_plain)

def signin(email: EmailStr, pwd: str):
    with eng.begin() as conn:
        real_pwd = conn.execute(select(users_table.c.pwd_hash).where(users_table.c.email == email)).scalar()
        if not real_pwd:
            return None
    if pwd_context.verify(pwd, real_pwd):
        # Generate User's Token
        with eng.begin() as conn:
            user_row = conn.execute(select(users_table).where(users_table.c.email == email)).mappings().first()
            if user_row["status"] != "Active":
                return -1
        payload = {"id": user_row["id"], "status": user_row["status"], "username": user_row["username"]}
        payload["exp"] = datetime.utcnow() + timedelta(hours=2)
        return jwt.encode(payload, settings.TOKEN_KEY, algorithm=settings.TOKEN_ALGO)
    else:
        return None


def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.TOKEN_KEY, algorithm=settings.TOKEN_ALGO)
        return payload
    except Exception as e:
        print(e)
        return None
