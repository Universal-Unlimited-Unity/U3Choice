from redis_client import redis
from database import eng
from sqlalchemy import select
from models.user_model import users_table
from database import eng
from .authentification import pwd_hash
async def refresh_user_cashe(username: str):
    cashed_keys = redis.smembers(f"profile_view_cache:{username}")
    if cashed_keys:
        for key in cashed_keys:
            redis.delete(key)
        redis.delete(f"profile_view_cache:{username}")
    if redis.exists(f"user:session:{username}"):
        redis.delete(f"user:session:{username}")

async def refresh_user_friends_cashe(username: str):
    if redis.exists(f"user:session:friends:{username}"):
            redis.delete(f"user:session:friends:{username}")
            
async def verify_pwd(user_id: str, pwd: str) -> bool:
    with eng.begin() as conn:
        stmt = select(users_table.c.pwd_hash).where(users_table.c.id == user_id)
        result = conn.execute(stmt).scalar()
        if result:
            if pwd_hash.verify(pwd, result):
                return True
        return False

async def update_cach_key(user1_id: str, user2_id: str, username1: str, username2: str):
    if redis.exists(f"user:session:{user1_id}:{username2}"):
        redis.delete(f"user:session:{user1_id}:{username2}")
    if redis.exists(f"user:session:{user2_id}:{username1}"):
        redis.delete(f"user:session:{user2_id}:{username1}")
    await refresh_user_friends_cashe(username1)
    await refresh_user_friends_cashe(username2)