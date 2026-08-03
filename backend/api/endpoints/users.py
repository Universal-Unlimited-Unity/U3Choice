from fastapi import APIRouter, HTTPException, Depends, Path, Body, Query
from services.users import get_user_profile_BY_USERNAME, get_profile_photo
from schemas.users_schema import Profile_View, User_Update
from redis_client import redis
import json
from typing import Annotated
from services.friendships import check_friendship_status, check_friendship_request_exists, is_blocked_friendship_exists
from schemas.users_schema import UserSummary
from services.users import get_friends_brief
from services.authentification import verify_token, username_used
from fastapi.responses import FileResponse
router = APIRouter(prefix="", tags=["users"])

@router.get("/{username}", response_model=Profile_View)
async def read_user_profile(username: Annotated[str, Path()], user: Annotated[dict, Depends(verify_token)]):
    viwer_id = user.get("id")
    
    cashed_profile = redis.get(f"user:session:{viwer_id}:{username}")
    if cashed_profile:
            return json.loads(cashed_profile)
    
    requested_profile = await get_user_profile_BY_USERNAME(username)
    if not requested_profile:
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile.status != "Active":
        raise HTTPException(status_code=403, detail="User is suspended")
    
    profile_view = Profile_View(viwed_id=str(requested_profile.id), 
                                username=requested_profile.username, 
                                viwer_id=str(viwer_id), 
                                is_owner=(str(requested_profile.id) == str(viwer_id)), 
                                name=requested_profile.name, 
                                bio=requested_profile.bio, 
                                country=requested_profile.country, 
                                verified=requested_profile.verified, 
                                status=requested_profile.status,
                                is_friends=await check_friendship_status(requested_profile.id, viwer_id),
                                has_sent_friendship_request=await check_friendship_request_exists(requested_profile.id, viwer_id),
                                has_received_friendship_request=await check_friendship_request_exists(viwer_id, requested_profile.id),
                                is_blocked=await is_blocked_friendship_exists(viwer_id, requested_profile.id))
    
    redis.set(f"user:session:{viwer_id}:{username}", json.dumps(profile_view.model_dump()), ex=3600)
    redis.sadd(f"profile_view_cache:{username}", f"user:session:{viwer_id}:{username}")    
    return profile_view

@router.get("/{username}/friends", response_model=UserSummary)
async def read_user_friends(username: Annotated[str, Path()], user: Annotated[dict, Depends(verify_token)]):
    viwer_id = user.get("id")
    requested_profile = await get_user_profile_BY_USERNAME(username)
    if not requested_profile:
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile.status != "Active":
        raise HTTPException(status_code=403, detail="User is suspended")
    if requested_profile.id != viwer_id:
        raise HTTPException(status_code=403, detail="You are not authorized to view this user's friends")
    
    friends_brief = await get_friends_brief(requested_profile.id)
    return friends_brief

@router.get("/{username}/photo")
async def get_profile_photo_endpoint(username: Annotated[str, Path()]):
    return FileResponse(await get_profile_photo(username), media_type="image/png")

@router.patch("/{username}/update", response_model=dict)
async def update_user_profile_endpoint(update_data: Annotated[User_Update, Body()], user: Annotated[dict, Depends(verify_token)]):
    if update_data.username and username_used(update_data.username):
        raise HTTPException(status_code=400, detail="USERNAME_TAKEN")
    
    