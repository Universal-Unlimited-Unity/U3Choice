from redis_client import redis
from database import eng
from sqlalchemy import select, update
from models.user_model import users_table
from database import eng
from .authentification import pwd_hash
from email.message import EmailMessage
import aiosmtplib

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

async def send_email_verification(to_email: str, code: int):
    msg = EmailMessage()
    msg["From"] = "adamaakif23@gmail.com"
    msg["To"] = to_email
    msg["Subject"] = "Email Verification"
    msg.set_content(f"Your verification code is: {code}")
    await aiosmtplib.send(msg, 
                          hostname="smtp.gmail.com", 
                          port=587, 
                          start_tls=True, 
                          username="adamaakif23@gmail.com", 
                          password="gqyz xmdj heph wlyg")

async def email_verification(username:str):
    with eng.begin() as conn:
        conn.execute(update(users_table).where(users_table.c.username == username).values(email_verified=True))
    await refresh_user_cashe(username)

async def update_pwd(email: str, new_pwd: str):
    hashed_pwd = pwd_hash.hash(new_pwd)
    with eng.begin() as conn:
        conn.execute(update(users_table).where(users_table.c.email == email).values(pwd_hash=hashed_pwd))
    
    