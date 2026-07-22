from redis_client import redis
from database import eng
from sqlalchemy import update
from models import users_table

def refresh_user_cashe(username: str):
    cashed_keys = redis.smembers(f"profile_view_cache:{username}")
    if cashed_keys:
        for key in cashed_keys:
            redis.delete(key)
        redis.delete(f"profile_view_cache:{username}")