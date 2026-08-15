from models.messages import messages_table
from schemas.messages import Message
from .friendships import get_friends
from database import eng
from sqlalchemy import insert, select

async def save_message(message: Message):
    if message.sender_id == message.receiver_id:
        raise ValueError("Sender and receiver cannot be the same user.")
    if message.sender_id not in await get_friends(message.receiver_id):
        raise ValueError("Sender and receiver must be friends.")
    with eng.begin() as conn:
        stmt = insert(messages_table).values(message.model_dump())
        conn.execute(stmt)

async def get_messages_between_users(user1_id, user2_id):
    with eng.begin() as conn:
        stmt = select(messages_table).where(
            ((messages_table.c.sender_id == user1_id) & (messages_table.c.receiver_id == user2_id)) |
            ((messages_table.c.sender_id == user2_id) & (messages_table.c.receiver_id == user1_id))
        ).order_by(messages_table.c.created_at.asc())
        messages = [dict(m) for m in conn.execute(stmt).mappings().all()]
        for m in messages:
            m["id"] = str(m["id"])
            m["sender_id"] = str(m["sender_id"])
            m["receiver_id"] = str(m["receiver_id"])
            m["created_at"] = str(m["created_at"])
        return messages