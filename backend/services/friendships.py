from redis_client import redis
from database import eng
from sqlalchemy import UUID, case, select, insert
from models.friendships_model import friendships_table
from schemas.friendships_schema import Friendships
from datetime import datetime, timezone
from models.friendships_model import blocked_friendships_table
from exceptions import FriendRequestNotFound, FriendshipAlreadyBlocked, FriendshipNotBlocked, SelfBlockError
from .security import refresh_user_friends_cashe
from .users import get_user_profile_BY_ID
from models.user_model import users_table

async def check_friendship_status(user1_id: UUID, user2_id: UUID) -> bool:
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

async def get_friends(user_id: UUID):
    with eng.begin() as conn:
        stmt = select(
            case(
                (friendships_table.c.sender_id == user_id,
                friendships_table.c.receiver_id),
                else_=friendships_table.c.sender_id
            )
        ).where(
            friendships_table.c.status == "Accepted"
        )
        result = conn.execute(stmt).scalars().all()
    return result

async def get_friends_brief(user_id: UUID):
    friends = await get_friends(user_id)
    with eng.begin() as conn:
        stmt = select(users_table.c.id, users_table.c.username, users_table.c.photo_url, 
                      users_table.c.name, users_table.c.country).where(users_table.c.id.in_(friends), users_table.c.status == "Active")
        result = conn.execute(stmt).mappings().all()
    result = [dict(user) for user in result]
    for user in result:
        user["id"] = str(user["id"])
    return result

async def check_friendship_request_exists(sender_id: UUID, receiver_id: UUID) -> bool:
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

async def send_friendship_request(friendship: Friendships, username1: str, username2: str):
    with eng.begin() as conn:
        dumped_friendship = friendship.model_dump()
        conn.execute(insert(friendships_table).values(dumped_friendship))
    if redis.exists(f"user:session:{friendship.sender_id}:{username1}"):
        redis.delete(f"user:session:{friendship.sender_id}:{username1}")
    if redis.exists(f"user:session:{friendship.receiver_id}:{username2}"):
        redis.delete(f"user:session:{friendship.receiver_id}:{username2}")

async def accept_friendship_request(sender_id: UUID, receiver_id: UUID, username1: str, username2: str):
    with eng.begin() as conn:
        stmt = select(1).where(
            friendships_table.c.sender_id == sender_id,
            friendships_table.c.receiver_id == receiver_id,
            friendships_table.c.status == "Pending"
        )
        result = conn.execute(stmt).first()
    if not result:
        raise FriendRequestNotFound("Friendship request not found")
    user1_profile = await get_user_profile_BY_ID(sender_id)
    user2_profile = await get_user_profile_BY_ID(receiver_id)
    await refresh_user_friends_cashe(user1_profile.username)
    await refresh_user_friends_cashe(user2_profile.username)

    with eng.begin() as conn:
        stmt = friendships_table.update().where(
            friendships_table.c.sender_id == sender_id,
            friendships_table.c.receiver_id == receiver_id
        ).values(status="Accepted", updated_at=datetime.now(timezone.utc))
        conn.execute(stmt)
    
    if redis.exists(f"user:session:{sender_id}:{username1}"):
        redis.delete(f"user:session:{sender_id}:{username1}")
    if redis.exists(f"user:session:{receiver_id}:{username2}"):
        redis.delete(f"user:session:{receiver_id}:{username2}")

async def reject_friendship_request(sender_id: UUID, receiver_id: UUID, username1: str, username2: str):
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
    
    if redis.exists(f"user:session:{sender_id}:{username1}"):
        redis.delete(f"user:session:{sender_id}:{username1}")
    if redis.exists(f"user:session:{receiver_id}:{username2}"):
        redis.delete(f"user:session:{receiver_id}:{username2}")

async def is_blocked_friendship_exists(user1_id: UUID, user2_id: UUID) -> bool:
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

async def block_friendship(blocker_id: UUID, blocked_id: UUID, username1: str, username2: str):
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
    with eng.begin() as conn:
        stmt = friendships_table.delete().where(
            ((friendships_table.c.sender_id == blocker_id) &
            (friendships_table.c.receiver_id == blocked_id)) |
            ((friendships_table.c.sender_id == blocked_id) &
            (friendships_table.c.receiver_id == blocker_id))
        )
        conn.execute(stmt)
    
    if redis.exists(f"user:session:{blocker_id}:{username1}"):
        redis.delete(f"user:session:{blocker_id}:{username1}")
    if redis.exists(f"user:session:{blocked_id}:{username2}"):
        redis.delete(f"user:session:{blocked_id}:{username2}")
    user1_profile = await get_user_profile_BY_ID(blocker_id)
    user2_profile = await get_user_profile_BY_ID(blocked_id)
    await refresh_user_friends_cashe(user1_profile.username)
    await refresh_user_friends_cashe(user2_profile.username)

async def unblock_friendship(blocker_id: UUID, blocked_id: UUID, username1: str, username2: str):
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
    
    if redis.exists(f"user:session:{blocker_id}:{username1}"):
        redis.delete(f"user:session:{blocker_id}:{username1}")
    if redis.exists(f"user:session:{blocked_id}:{username2}"):
        redis.delete(f"user:session:{blocked_id}:{username2}")
    user1_profile = await get_user_profile_BY_ID(blocker_id)
    user2_profile = await get_user_profile_BY_ID(blocked_id)
    await refresh_user_friends_cashe(user1_profile.username)
    await refresh_user_friends_cashe(user2_profile.username)

async def remove_friendship(friendship: Friendships, username1: str, username2: str):
    with eng.begin() as conn:
        stmt = select(1).where(
            ((friendships_table.c.sender_id == friendship.sender_id) &
            (friendships_table.c.receiver_id == friendship.receiver_id)) |
            ((friendships_table.c.sender_id == friendship.receiver_id) &
            (friendships_table.c.receiver_id == friendship.sender_id))
        )
        result = conn.execute(stmt).first()
    if not result:
        raise FriendRequestNotFound("Friendship not found")
    
    with eng.begin() as conn:
        stmt = friendships_table.delete().where(
            ((friendships_table.c.sender_id == friendship.sender_id) &
            (friendships_table.c.receiver_id == friendship.receiver_id)) |
            ((friendships_table.c.sender_id == friendship.receiver_id) &
            (friendships_table.c.receiver_id == friendship.sender_id))
        )
        conn.execute(stmt)
    
    if redis.exists(f"user:session:{friendship.sender_id}:{username1}"):
        redis.delete(f"user:session:{friendship.sender_id}:{username1}")
    if redis.exists(f"user:session:{friendship.receiver_id}:{username2}"):
        redis.delete(f"user:session:{friendship.receiver_id}:{username2}")
    user1_profile = await get_user_profile_BY_ID(friendship.sender_id)
    user2_profile = await get_user_profile_BY_ID(friendship.receiver_id)    
    await refresh_user_friends_cashe(user1_profile.username)
    await refresh_user_friends_cashe(user2_profile.username)