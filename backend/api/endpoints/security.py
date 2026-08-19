from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from services.authentification import verify_token
from services.security import send_email_verification
from services.users import get_user_profile_BY_EMAIL, get_user_profile_BY_ID
import random
import asyncio
from services.security import email_verification, update_pwd
from services.authentification import pwd_hash
from typing import Annotated

router = APIRouter(prefix="/security", tags=["security"])

store_codes = {}
@router.post("/send_verification_email")
async def send_verification_email_endpoint(background_tasks: BackgroundTasks, token: Annotated[dict, Depends(verify_token)]):
    user = await get_user_profile_BY_ID(token.get("id"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.status != "Active":
        raise HTTPException(status_code=403, detail="User is suspended")
    email = user.email
    code = random.randint(1000, 9999)
    if email in store_codes:
        del store_codes[email]
    store_codes[email] = code
    background_tasks.add_task(send_email_verification, user.email, code)
    return {"message": "Verification email sent successfully"}

@router.post("/verify_email_code")
async def verify_email_code_endpoint(code: int, token: Annotated[dict, Depends(verify_token)]):
    user = await get_user_profile_BY_ID(token.get("id"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.status != "Active":
        raise HTTPException(status_code=403, detail="User is suspended")
    email = user.email
    if email not in store_codes or store_codes[email] != code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    del store_codes[email]
    await email_verification(user.username)
    return {"message": "Email verified successfully"}

@router.post("/send_verification_email_forgot_password")
async def send_verification_email_endpoint(background_tasks: BackgroundTasks, email: str):
    user = await get_user_profile_BY_EMAIL(email)
    if not user:
        return {"message": "If the email exists, a verification code has been sent."}
    if user.status != "Active":
        raise HTTPException(status_code=403, detail="User is suspended")
    email = user.email
    code = random.randint(1000, 9999)
    if email in store_codes:
        del store_codes[email]
    store_codes[email] = code
    background_tasks.add_task(send_email_verification, user.email, code)
    return {"message": "If the email exists, a verification code has been sent."}

@router.get("/forgot_password")
async def forgot_password_endpoint(email: str, code: int, new_password: str):
    if email not in store_codes or store_codes[email] != code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    del store_codes[email]
    new_password_hashed = pwd_hash.hash(new_password)
    await update_pwd(email, new_password_hashed)
    return {"message": "Password updated successfully"}

