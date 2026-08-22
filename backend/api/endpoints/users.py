import uuid
from fastapi import APIRouter, HTTPException, Depends, Path, Body, Query, File, UploadFile
from services.users import get_user_profile_BY_USERNAME, get_profile_photo, change_pwd, change_email, change_phone
from schemas.users_schema import Profile_View, User_Update, old_pwd, new_pwd, new_email, UserSummary, new_phone, Profile_View_Without_email_verified
from redis_client import redis
import json
from typing import Annotated, Any
from services.friendships import check_friendship_status, check_friendship_request_exists, is_blocked_friendship_exists, get_friends_brief, did_they_blocked_me
from services.users import update_user_profile, update_user_profile_photo
from services.authentification import verify_token, username_used
from fastapi.responses import FileResponse
import shutil
from pathlib import Path
from services.security import verify_pwd
from services.authentification import pwd_strong
import logging
router = APIRouter(prefix="", tags=["users"])

logger = logging.getLogger(__name__)
@router.get("/{username}")
async def read_user_profile(username: Annotated[str, Path()], user: Annotated[dict, Depends(verify_token)]):
    viwer_id = user.get("id")
    if user.get("status") != "Active":
        logger.warning("User with ID %s is not active", viwer_id)
        raise HTTPException(status_code=403, detail="Your account is suspended")
    username = username.lower()
    requested_profile = await get_user_profile_BY_USERNAME(username)
    if not requested_profile:
        logger.warning("User profile for username %s not found", username)
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile.status != "Active":
        logger.warning("User profile for username %s is not active", username)
        raise HTTPException(status_code=403, detail="User is suspended")
    cashed_profile = redis.get(f"user:session:{viwer_id}:{username}")
    if cashed_profile:
            return json.loads(cashed_profile)
    
    profile_view = Profile_View(viwed_id=str(requested_profile.id), 
                                username=requested_profile.username, 
                                viwer_id=str(viwer_id), 
                                is_owner=(str(requested_profile.id) == str(viwer_id)), 
                                name=requested_profile.name, 
                                bio=requested_profile.bio, 
                                country=requested_profile.country, 
                                verified=requested_profile.verified, 
                                status=requested_profile.status,
                                is_friends=await check_friendship_status(requested_profile.id, uuid.UUID(viwer_id)),
                                has_sent_friendship_request=await check_friendship_request_exists(requested_profile.id, uuid.UUID(viwer_id)),
                                has_received_friendship_request=await check_friendship_request_exists(uuid.UUID(viwer_id), requested_profile.id),
                                they_blocked_me=await did_they_blocked_me(uuid.UUID(viwer_id), requested_profile.id),
                                i_blocked_them=await did_they_blocked_me(requested_profile.id, uuid.UUID(viwer_id)),
                                email_verified=requested_profile.email_verified)
    
    if not profile_view.is_owner:
        profile_view = Profile_View_Without_email_verified(**profile_view.dict())

    redis.set(f"user:session:{viwer_id}:{username}", json.dumps(profile_view.model_dump()), ex=3600)
    redis.sadd(f"profile_view_cache:{username}", f"user:session:{viwer_id}:{username}")    
    return profile_view


@router.get("/{username}/friends", response_model=dict[str, Any])
async def read_user_friends(username: Annotated[str, Path()], user: Annotated[dict, Depends(verify_token)]):
    if username != user.get("username"):
        logger.warning("User with ID %s is not authorized to view friends of username %s", user.get("id"), username)
        raise HTTPException(status_code=403, detail="You are not authorized to view this user's friends")
    if user.get("status") != "Active":
        logger.warning("User with ID %s is not active", user.get("id"))
        raise HTTPException(status_code=403, detail="Your account is suspended")
    viwer_id = user.get("id")
    requested_profile = await get_user_profile_BY_USERNAME(username)
    if not requested_profile:
        logger.warning("User profile for username %s not found", username)
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile.status != "Active":
        logger.warning("User profile for username %s is not active", username)
        raise HTTPException(status_code=403, detail="User is suspended")
    
    if redis.exists(f"user:session:friends:{username}"):
        return {"friends": json.loads(redis.get(f"user:session:friends:{username}")), "total": len(json.loads(redis.get(f"user:session:friends:{username}")))}
    friends_brief = await get_friends_brief(requested_profile.id)
    redis.set(f"user:session:friends:{username}", json.dumps(friends_brief), ex=3600)
    return {"friends": friends_brief, "total": len(friends_brief)}
    
@router.get("/{username}/photo")
async def get_profile_photo_endpoint(username: Annotated[str, Path()], user: Annotated[dict, Depends(verify_token)]):
    if user.get("status") != "Active":
        logger.warning("User with ID %s is not active", user.get("id"))
        raise HTTPException(status_code=403, detail="Your account is suspended")
    requested_profile = await get_user_profile_BY_USERNAME(username)
    if not requested_profile:
        logger.warning("User profile for username %s not found", username)
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile.status != "Active":
        logger.warning("User profile for username %s is not active", username)
        raise HTTPException(status_code=403, detail="User is suspended")
    return FileResponse(await get_profile_photo(username), media_type="image/png")

@router.patch("/{username}/update", response_model=dict[str, Any])
async def update_user_profile_endpoint(username: Annotated[str, Path()], update_data: Annotated[User_Update, Body()], user: Annotated[dict, Depends(verify_token)]):
    if user.get("status") != "Active":
        logger.warning("User with ID %s is not active", user.get("id"))
        raise HTTPException(status_code=403, detail="Your account is suspended")
    requested_profile = await get_user_profile_BY_USERNAME(username)
    if not requested_profile:
        logger.warning("User profile for username %s not found", username)
        raise HTTPException(status_code=404, detail="User not found")
    if username != user.get("username"):
        logger.warning("User with ID %s is not authorized to update profile for username %s", user.get("id"), username)
        raise HTTPException(status_code=403, detail="You are not authorized to update this user's profile")
    if update_data.username and username_used(update_data.username):
        logger.warning("Username %s is already taken", update_data.username)
        raise HTTPException(status_code=400, detail="USERNAME_TAKEN")
    logger.info("User with ID %s updated profile for username %s", user.get("id"), username)
    return {"token": await update_user_profile(update_data, username, update_data.username if update_data.username else None), 
            "message": "Profile updated successfully"}

@router.patch("/{username}/update/photo", response_model=dict[str, Any])
async def update_user_profile_photo_endpoint(username: Annotated[str, Path()], photo: Annotated[UploadFile, File()], user: Annotated[dict, Depends(verify_token)]):
    if user.get("status") != "Active":
        logger.warning("User with ID %s is not active", user.get("id"))
        raise HTTPException(status_code=403, detail="Your account is suspended")
    requested_profile = await get_user_profile_BY_USERNAME(username)
    if not requested_profile:
        logger.warning("User profile for username %s not found", username)
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile.status != "Active":
        logger.warning("User profile for username %s is not active", username)
        raise HTTPException(status_code=403, detail="User is suspended")
    if username != user.get("username"):
        logger.warning("User with ID %s is not authorized to update profile photo for username %s", user.get("id"), username)
        raise HTTPException(status_code=403, detail="You are not authorized to update this user's profile photo")
    if photo.content_type not in ["image/jpeg", "image/png"]:
        logger.warning("Invalid file type for username %s. Only JPEG and PNG are allowed.", username)
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")
    BASE_DIR = Path("assets/profile_photos")
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    file_path = BASE_DIR / f"{user.get('username')}_{photo.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)
    logger.info("Profile photo updated for username %s", user.get("username"))
    return {"token": await update_user_profile_photo(user.get("username"), str(file_path)), 
            "message": "Profile photo updated successfully"}
    

@router.post("/settings/password")
async def get_user_settings(old_pwd: Annotated[old_pwd, Body()], new_pwd: Annotated[new_pwd, Body()], user: Annotated[dict, Depends(verify_token)]):    
    if user.get("status") != "Active":
        logger.warning("User with ID %s is not active", user.get("id"))
        raise HTTPException(status_code=403, detail="Your account is suspended")
    if not await verify_pwd(user.get("id"), old_pwd.old_pwd):
        logger.warning("Invalid password for user with ID %s", user.get("id"))
        raise HTTPException(status_code=403, detail="Invalid password")
    if new_pwd.new_pwd == old_pwd.old_pwd:
        logger.warning("New password cannot be the same as the old password for user with ID %s", user.get("id"))
        raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")
    if not pwd_strong(new_pwd.new_pwd):
        logger.warning("New password for user with ID %s is not strong enough", user.get("id"))
        raise HTTPException(status_code=400, detail="New password is not strong enough, include at least 8 characters, one number and one special character")
    requested_profile = await get_user_profile_BY_USERNAME(user.get("username"))
    if not requested_profile:
        logger.warning("User profile for username %s not found", user.get("username"))
        raise HTTPException(status_code=404, detail="User not found")
    await change_pwd(user.get("id"), old_pwd.old_pwd, new_pwd.new_pwd)
    logger.info("Password changed successfully for user with ID %s", user.get("id"))
    return {"message": "Password changed successfully"}

@router.post("/settings/email")
async def get_user_settings_email(pwd: Annotated[old_pwd, Body()], new_email: Annotated[new_email, Body()], user: Annotated[dict, Depends(verify_token)]):    
    if user.get("status") != "Active":
        logger.warning("User with ID %s is not active", user.get("id"))
        raise HTTPException(status_code=403, detail="Your account is suspended")
    if not await verify_pwd(user.get("id"), pwd.old_pwd.lower()):
        logger.warning("Invalid password for user with ID %s", user.get("id"))
        raise HTTPException(status_code=403, detail="Invalid password")
    requested_profile = await get_user_profile_BY_USERNAME(user.get("username"))
    if not requested_profile:
        logger.warning("User profile for username %s not found", user.get("username"))
        raise HTTPException(status_code=404, detail="User not found")
    await change_email(user.get("id"), new_email.new_email)
    logger.info("Email changed successfully for user with ID %s", user.get("id"))
    return {"message": "Email changed successfully"}

@router.post("/settings/phone")
async def get_user_settings_phone(pwd: Annotated[old_pwd, Body()], new_phone: Annotated[new_phone, Body()], user: Annotated[dict, Depends(verify_token)]):    
    if user.get("status") != "Active":
        logger.warning("User with ID %s is not active", user.get("id"))
        raise HTTPException(status_code=403, detail="Your account is suspended")
    if not await verify_pwd(user.get("id"), pwd.old_pwd.lower()):
        logger.warning("Invalid password for user with ID %s", user.get("id"))
        raise HTTPException(status_code=403, detail="Invalid password")
    requested_profile = await get_user_profile_BY_USERNAME(user.get("username"))
    if not requested_profile:
        logger.warning("User profile for username %s not found", user.get("username"))
        raise HTTPException(status_code=404, detail="User not found")
    await change_phone(user.get("id"), new_phone.new_phone)
    logger.info("Phone number changed successfully for user with ID %s", user.get("id"))
    return {"message": "Phone number changed successfully"}

