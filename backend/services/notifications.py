from sqlalchemy import insert, select
from database import eng
from models.notifications import notification_table
from schemas.notifications import Notification
from redis_client import redis
import json

async def save_notification(notification: Notification):
    with eng.begin() as conn:
        stmt = insert(notification_table).values(notification.model_dump())
        conn.execute(stmt)
    if redis.exists(f"notifications:{notification.concerned_id}"):
        redis.delete(f"notifications:{notification.concerned_id}")

async def get_notifications_for_user(user_id):
    if redis.exists(f"notifications:{user_id}"):
        return json.loads(redis.get(f"notifications:{user_id}"))
    
    with eng.begin() as conn:
        stmt = select(notification_table).where(notification_table.c.concerned_id == user_id)
        notifications = [dict(n) for n in conn.execute(stmt).mappings().all()]
        for n in notifications:
            n["id"] = str(n["id"])
            n["root_id"] = str(n["root_id"])
            n["concerned_id"] = str(n["concerned_id"])
            n["created_at"] = str(n["created_at"])
        redis.set(f"notifications:{user_id}", json.dumps([dict(n) for n in notifications]))
        return notifications