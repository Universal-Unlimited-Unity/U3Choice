from database import eng
from sqlalchemy import select
from models.user_model import users_table
from password_validator import PasswordValidator

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
    
