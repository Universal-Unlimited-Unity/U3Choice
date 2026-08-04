from sqlalchemy import select, update
from .authentification import generate_token_by_username
from database import eng
from models.user_model import users_table
from schemas.users_schema import User_Profile, User_Update
from uuid import UUID
from .friendships import get_friends
from .security import refresh_user_cashe
from .security import verify_pwd
from .authentification import pwd_hash
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
                      users_table.c.name, users_table.c.country).where(users_table.c.id.in_(friends))
        result = conn.execute(stmt).mappings().all()
    return result

async def get_profile_photo(username: str):
    user = await get_user_profile_BY_USERNAME(username)
    return user.photo_url

async def update_user_profile(update_data: User_Update, username: str):
    if not update_data.model_dump(exclude_unset=True):
        return None
    with eng.begin() as conn:
        stmt = update(users_table).where(users_table.c.username == username).values(update_data.model_dump())
        conn.execute(stmt)
    
    await refresh_user_cashe(username)
    return generate_token_by_username(username)


async def update_user_profile_photo(username: str, photo_url: str):
    with eng.begin() as conn:
        stmt = update(users_table).where(users_table.c.username == username).values({"photo_url": photo_url})
        conn.execute(stmt)
    
    await refresh_user_cashe(username)
    return generate_token_by_username(username)

async def change_pwd(user_id: str, old_pwd: str, new_pwd: str):
    if not await verify_pwd(user_id, old_pwd):
        return None
    hashed_pwd = pwd_hash.hash(new_pwd)
    with eng.begin() as conn:
        stmt = update(users_table).where(users_table.c.id == user_id).values({"pwd_hash": hashed_pwd})
        conn.execute(stmt)
    return True

async def change_email(user_id: str, new_email: str):
    with eng.begin() as conn:
        stmt = update(users_table).where(users_table.c.id == user_id).values({"email": new_email})
        conn.execute(stmt)
    return True

async def change_phone(user_id: str, new_phone: str):
    with eng.begin() as conn:
        stmt = update(users_table).where(users_table.c.id == user_id).values({"phone": new_phone})
        conn.execute(stmt)
    return True