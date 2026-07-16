from sqlalchemy import select
from backend.database import eng
from backend.models import users_table
from backend.schemas.users_schema import User_Profile
from uuid import UUID
from .friendships import get_friends
def get_user_profile_BY_ID(id):
    with eng.begin() as conn:
        stmt = select(users_table).where(users_table.c.id == id)
        user = conn.execute(stmt).mappings().first()
        user = User_Profile(**user)
        return user
    
def get_user_profile_BY_USERNAME(username):
    with eng.begin() as conn:
        stmt = select(users_table).where(users_table.c.username == username)
        user = conn.execute(stmt).mappings().first()
        user = User_Profile(**user)
        return user
    
def get_friends_brief(user_id: UUID):
    friends = get_friends(user_id)
    with eng.begin() as conn:
        stmt = select(users_table.c.id, users_table.c.username, users_table.photo_url, 
                      users_table.c.name).where(users_table.c.id.in_(friends))
        result = conn.execute(stmt).mappings().all()