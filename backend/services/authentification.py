from database import eng
from sqlalchemy import select, insert
from models.user_model import users_table
from password_validator import PasswordValidator
from schemas.users_schema import User, User_token
from passlib.context import CryptContext
from pydantic import EmailStr
from jose import jwt
from datetime import datetime, timedelta
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
    if pwd_context.verify(pwd, real_pwd):
        # Generate User's Token
        with eng.begin() as conn:
            user_row = conn.execute(select(users_table).where(users_table.c.email == email)).mappings().first()
        payload = (User_token(**user_row)).model_dump()
        payload["exp"] = datetime.utcnow() + timedelta(hours=2)
        


