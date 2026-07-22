from redis_client import redis
from database import eng
from sqlalchemy import UUID, Case, select, insert
from models.friendships_model import friendships_table
from schemas.friendships_schema import Friendships
from datetime import datetime, timezone
from models.friendships_model import blocked_friendships_table
from exceptions import FriendRequestNotFound, FriendshipAlreadyBlocked, FriendshipNotBlocked, SelfBlockError
def check_friendship_status(user1_id: UUID, user2_id: UUID) -> bool:
    with eng.begin() as conn:
        stmt = select(1).where(
            friendships_table.c.status == "Accepted",
            (
                (
                    (friendships_table.c.sender_id == user1_id) &
                    (friendships_table.c.receiver_id == user2_id)
                )
                |
                (
                    (friendships_table.c.sender_id == user2_id) &
                    (friendships_table.c.receiver_id == user1_id)
                )
            )
        )

        result = conn.execute(stmt).first()
    if result:
        return True
    return False

def get_friends(user_id: UUID):
    with eng.begin() as conn:
        stmt = select(
            Case(
                (friendships_table.c.sender_id == user_id),
                friendships_table.c.receiver_id,
                else_=friendships_table.c.sender_id
            )
        ).where(
            friendships_table.c.status == "Accepted"
        )
        result = conn.execute(stmt).scalars().all()
    return result

def check_friendship_request_exists(sender_id: UUID, receiver_id: UUID) -> bool:
    if sender_id == receiver_id:
        return False
    with eng.begin() as conn:
        stmt = select(1).where(
            friendships_table.c.status == "Pending",
            friendships_table.c.sender_id == sender_id,
            friendships_table.c.receiver_id == receiver_id
        )
        result = conn.execute(stmt).first()
    if result:
        return True
    return False

def send_friendship_request(friendship: Friendships):
    with eng.begin() as conn:
        dumped_friendship = friendship.model_dump()
        conn.execute(insert(friendships_table).values(dumped_friendship))
    if redis.exists(f"user:session:{friendship.sender_id}:{friendship.receiver_id}"):
        redis.delete(f"user:session:{friendship.sender_id}:{friendship.receiver_id}")
    if redis.exists(f"user:session:{friendship.receiver_id}:{friendship.sender_id}"):
        redis.delete(f"user:session:{friendship.receiver_id}:{friendship.sender_id}")

def accept_friendship_request(sender_id: UUID, receiver_id: UUID):
    with eng.begin() as conn:
        stmt = select(1).where(
            friendships_table.c.sender_id == sender_id,
            friendships_table.c.receiver_id == receiver_id,
            friendships_table.c.status == "Pending"
        )
        result = conn.execute(stmt).first()
    if not result:
        raise FriendRequestNotFound("Friendship request not found")

    with eng.begin() as conn:
        stmt = friendships_table.update().where(
            friendships_table.c.sender_id == sender_id,
            friendships_table.c.receiver_id == receiver_id
        ).values(status="Accepted", updated_at=datetime.now(timezone.utc))
        conn.execute(stmt)
    
    if redis.exists(f"user:session:{sender_id}:{receiver_id}"):
        redis.delete(f"user:session:{sender_id}:{receiver_id}")
    if redis.exists(f"user:session:{receiver_id}:{sender_id}"):
        redis.delete(f"user:session:{receiver_id}:{sender_id}")

def reject_friendship_request(sender_id: UUID, receiver_id: UUID):
    with eng.begin() as conn:
        stmt = select(1).where(
            friendships_table.c.sender_id == sender_id,
            friendships_table.c.receiver_id == receiver_id,
            friendships_table.c.status == "Pending"
        )
        result = conn.execute(stmt).first()
    if not result:
        raise FriendRequestNotFound("Friendship request not found")
    
    with eng.begin() as conn:
        stmt = friendships_table.delete().where(
            friendships_table.c.sender_id == sender_id,
            friendships_table.c.receiver_id == receiver_id
        )
        conn.execute(stmt)
    
    if redis.exists(f"user:session:{sender_id}:{receiver_id}"):
        redis.delete(f"user:session:{sender_id}:{receiver_id}")
    if redis.exists(f"user:session:{receiver_id}:{sender_id}"):
        redis.delete(f"user:session:{receiver_id}:{sender_id}")

def is_blocked_friendship_exists(user1_id: UUID, user2_id: UUID) -> bool:
    with eng.begin() as conn:
        stmt = select(1).where(
            ((blocked_friendships_table.c.blocker_id == user1_id) &
            (blocked_friendships_table.c.blocked_id == user2_id)) |
            ((blocked_friendships_table.c.blocker_id == user2_id) &
            (blocked_friendships_table.c.blocked_id == user1_id))
        )
        result = conn.execute(stmt).first()
    if result:
        return True
    return False

def block_friendship(blocker_id: UUID, blocked_id: UUID):
    if blocker_id == blocked_id:
        raise SelfBlockError("Cannot block yourself")
    with eng.begin() as conn:
        stmt = select(1).where(
            ((blocked_friendships_table.c.blocker_id == blocker_id) &
            (blocked_friendships_table.c.blocked_id == blocked_id)) |
            ((blocked_friendships_table.c.blocker_id == blocked_id) &
            (blocked_friendships_table.c.blocked_id == blocker_id))
        )
        result = conn.execute(stmt).first()
    if result:
        raise FriendshipAlreadyBlocked("Friendship already blocked")
    
    with eng.begin() as conn:
        stmt = insert(blocked_friendships_table).values(
            blocker_id=blocker_id,
            blocked_id=blocked_id,
            created_at=datetime.now(timezone.utc)
        )
        conn.execute(stmt)
    
    if redis.exists(f"user:session:{blocker_id}:{blocked_id}"):
        redis.delete(f"user:session:{blocker_id}:{blocked_id}")
    if redis.exists(f"user:session:{blocked_id}:{blocker_id}"):
        redis.delete(f"user:session:{blocked_id}:{blocker_id}")
    
def unblock_friendship(blocker_id: UUID, blocked_id: UUID):
    if blocker_id == blocked_id:
        raise SelfBlockError("Cannot unblock yourself")
    with eng.begin() as conn:
        stmt = select(1).where(
            ((blocked_friendships_table.c.blocker_id == blocker_id) &
            (blocked_friendships_table.c.blocked_id == blocked_id)) |
            ((blocked_friendships_table.c.blocker_id == blocked_id) &
            (blocked_friendships_table.c.blocked_id == blocker_id))
        )
        result = conn.execute(stmt).first()
    if not result:
        raise FriendshipNotBlocked("Friendship not blocked")
    
    with eng.begin() as conn:
        stmt = blocked_friendships_table.delete().where(
            ((blocked_friendships_table.c.blocker_id == blocker_id) &
            (blocked_friendships_table.c.blocked_id == blocked_id)) |
            ((blocked_friendships_table.c.blocker_id == blocked_id) &
            (blocked_friendships_table.c.blocked_id == blocker_id))
        )
        conn.execute(stmt)
    
    if redis.exists(f"user:session:{blocker_id}:{blocked_id}"):
        redis.delete(f"user:session:{blocker_id}:{blocked_id}")
    if redis.exists(f"user:session:{blocked_id}:{blocker_id}"):
        redis.delete(f"user:session:{blocked_id}:{blocker_id}")

