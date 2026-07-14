from sqlalchemy import select
from backend.database import eng
from backend.models import users_table
from backend.schemas.users_schema import User_Profile

def get_user_profile(id):
    with eng.begin() as conn:
        stmt = select(users_table).where(users_table.c.id == id)
        user = conn.execute(stmt).mappings().first()
        user = User_Profile(**user)
        return user
    