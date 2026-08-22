from fastapi import APIRouter, HTTPException, Body, Query
from services.authentification import signup, signin, username_used, email_used, pwd_strong, hash_pwd,  verify_age 
from schemas.users_schema import User
from typing import Annotated
from schemas.authentification import credentials
import logging

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["authentification"])

@auth_router.post("/signup")
async def signup_endpoint(user: Annotated[User, Body()]):
    if username_used(user.username.lower()):
        logger.warning("Username %s already exists in the Database", user.username.lower())
        raise HTTPException(status_code=400, detail="USERNAME_TAKEN")
    if email_used(user.email.lower()):
        logger.warning("Email %s already exists in the Database", user.email.lower())
        raise HTTPException(status_code=400, detail="EMAIL_TAKEN")
    if not pwd_strong(user.pwd_hash.lower()):
        logger.warning("Password for user %s is not strong enough", user.username.lower())
        raise HTTPException(status_code=400, detail="PASSWORD_NOT_STRONG")
    if not verify_age(user.dob):
        logger.warning("User %s is underage", user.username.lower())
        raise HTTPException(status_code=400, detail="USER_UNDERAGE")
    user.pwd_hash = hash_pwd(user.pwd_hash.lower())
    user.username = user.username.lower()
    user.email = user.email.lower()
    signup(user)
    logger.info("User %s created successfully", user.username.lower())
    return {"message": "User created successfully"}

@auth_router.post("/signin")
async def signin_endpoint(credentials: Annotated[credentials, Body()]):
    token = signin(credentials.email.lower(), credentials.pwd.lower(), credentials.last_login)
    if not token:
        logger.warning("Invalid credentials for email %s", credentials.email.lower())
        raise HTTPException(status_code=400, detail="INVALID_CREDENTIALS")
    if token == -1:
        logger.warning("User with email %s is suspended", credentials.email.lower())
        raise HTTPException(status_code=403, detail="USER_SUSPENDED")
    logger.info("User with email %s signed in successfully", credentials.email.lower())
    return {"token": token, "type": "bearer"}
