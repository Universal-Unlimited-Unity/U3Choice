from fastapi import APIRouter, HTTPException, HTTPRes
from services.authentification import signup, signin, decode_token, username_used, email_used, pwd_strong, hash_pwd
from scheæas.users_schema import User

users_router = APIRouter(tags=["users"])

@users_router.post("/signup")
async def signup(user: User):
    if username_used(user.username):
        raise HTTPException(status_code=400, detail="USERNAME_TAKEN")
    if email_used(user.email):
        raise HTTPException(status_code=400, detail="EMAIL_TAKEN")
    if not pwd_strong(user.pwd_hash):
        raise HTTPException(status_code=400, detail="PASSWORD_NOT_STRONG")
    user.pwd_hash = hash_pwd(user.pwd_hash)
    signup(user)
    return {"message": "User created successfully"}

@users_router.post("/signin")
async def signin(email: str, pwd: str):
    token = signin(email, pwd)
    if not token:
        raise HTTPException(status_code=400, detail="INVALID_CREDENTIALS")
    return {"token": token}