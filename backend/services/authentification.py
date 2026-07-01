from database import eng
from sqlalchemy import select
from models.user_model import users_table
def username_used(username: str) -> bool:
    with eng.connect() as conn:
        stmt = select(users_table).where(users_table.c.id == username)
        result = conn.execute(stmt).fetchone()
        if result:
            return True
        return False
