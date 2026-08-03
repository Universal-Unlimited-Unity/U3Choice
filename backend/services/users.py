from sqlalchemy import select, update
from .authentification import generate_token
from database import eng
from models.user_model import users_table
from schemas.users_schema import User_Profile, User_Update
from uuid import UUID
from .friendships import get_friends
from redis_client import redis
from .security import refresh_user_cashe

async def get_user_profile_BY_ID(id):
    with eng.begin() as conn:
        stmt = select(users_table).where(users_table.c.id == id)
        user = conn.execute(stmt).mappings().first()
        user = User_Profile(**user)
        return user
    
async def get_user_profile_BY_USERNAME(username):
    with eng.begin() as conn:
        stmt = select(users_table).where(users_table.c.username == username)
        user = conn.execute(stmt).mappings().first()
        user = User_Profile(**user)
        return user

async def get_friends_brief(user_id: UUID):
    friends = await get_friends(user_id)
    with eng.begin() as conn:
        stmt = select(users_table.c.id, users_table.c.username, users_table.photo_url, 
                      users_table.c.name).where(users_table.c.id.in_(friends))
        result = conn.execute(stmt).mappings().all()
    return result

async def get_profile_photo(username: str):
    user = await get_user_profile_BY_USERNAME(username)
    return user.photo_url

async def update_user_profile(update_data: User_Update, username: str, email: str):
    if not update_data.model_dump(exclude_unset=True):
        return None
    with eng.begin() as conn:
        stmt = update(users_table).where(users_table.c.username == username).values(update_data.model_dump())
        conn.execute(stmt)
    
    await refresh_user_cashe(username)
    return generate_token(email)

    