from backend.redis import redis
from backend.database import eng
from sqlalchemy import update
from backend.models import users_table

def suspend_user(user_id):
    with eng.begin() as conn:
        stmt = update(users_table).where(users_table.c.id == user_id).values(status="Suspended")
        conn.execute(stmt)
        redis.delete(f"user:session:{user_id}")