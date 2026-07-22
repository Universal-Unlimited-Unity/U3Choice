from fastapi import APIRouter, HTTPException, Body, Query
from services.authentification import signup, signin, username_used, email_used, pwd_strong, hash_pwd
from schemas.users_schema import User
from typing import Annotated
from schemas.authentification import credentials
auth_router = APIRouter(prefix="/auth", tags=["authentification"])

@auth_router.post("/signup")
async def signup_endpoint(user: Annotated[User, Body()]):
    if username_used(user.username):
        raise HTTPException(status_code=400, detail="USERNAME_TAKEN")
    if email_used(user.email):
        raise HTTPException(status_code=400, detail="EMAIL_TAKEN")
    if not pwd_strong(user.pwd_hash):
        raise HTTPException(status_code=400, detail="PASSWORD_NOT_STRONG")
    user.pwd_hash = hash_pwd(user.pwd_hash)
    signup(user)
    return {"message": "User created successfully"}

@auth_router.post("/signin")
async def signin_endpoint(credentials: Annotated[credentials, Body()]):
    token = signin(credentials.email, credentials.pwd)
    if not token:
        raise HTTPException(status_code=400, detail="INVALID_CREDENTIALS")
    if token == -1:
        raise HTTPException(status_code=403, detail="USER_SUSPENDED")
    return {"token": token, "type": "bearer"}