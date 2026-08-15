from sqlalchemy import select, update, func
from .authentification import generate_token_by_username
from database import eng
from models.user_model import users_table
from schemas.users_schema import User_Profile, User_Update
from uuid import UUID
from .security import refresh_user_cashe
from .security import verify_pwd
from .authentification import pwd_hash

async def get_user_profile_BY_ID(id):
    with eng.begin() as conn:
        stmt = select(users_table).where(users_table.c.id == id)
        user = conn.execute(stmt).mappings().first()
        if not user:
            return None
        user = User_Profile(**user)
        return user
    
async def get_users_by_ids(ids):
    with eng.begin() as conn:
        stmt = select(users_table).where(users_table.c.id.in_(ids))
        users = conn.execute(stmt).mappings().all()
        return [User_Profile(**user) for user in users]
        
async def get_user_profile_BY_USERNAME(username):
    with eng.begin() as conn:
        stmt = select(users_table).where(users_table.c.username == username)
        user = conn.execute(stmt).mappings().first()
        if not user:
            return None
        user = User_Profile(**user)
        return user

async def get_profile_photo(username: str):
    user = await get_user_profile_BY_USERNAME(username)
    return user.photo_url

async def update_user_profile(update_data: User_Update, username: str, new_username: str = None):
    if not update_data.model_dump(exclude_unset=True):
        return None
    with eng.begin() as conn:
        stmt = update(users_table).where(users_table.c.username == username).values(update_data.model_dump(exclude_none=True))
        conn.execute(stmt)
    
    await refresh_user_cashe(new_username if new_username else username)
    return generate_token_by_username(new_username if new_username else username)


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
