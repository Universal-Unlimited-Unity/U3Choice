from fastapi import APIRouter, HTTPException, Depends, Path, Body, Query
from backend.services.users import get_user_profile_BY_USERNAME
from backend.schemas.users_schema import Profile_View
from backend.redis import redis
import json
import jwt
from typing import Annotated
from backend.services.friendships import check_friendship_status, check_friendship_request_exists, is_blocked_friendship_exists
from backend.schemas.users_schema import UserSummary
from backend.services.users import get_friends_brief
from backend.services.authentification import verify_token

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{username}", response_model=Profile_View)
def read_user_profile(username: Annotated[str, Path()], user: Annotated[dict, Depends(verify_token)]):
    viwer_id = user.get("id")
    
    cashed_profile = redis.get(f"user:session:{viwer_id}:{username}")
    if cashed_profile:
            return json.loads(cashed_profile)
    
    requested_profile = get_user_profile_BY_USERNAME(username)
    if not requested_profile:
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile.status != "Active":
        raise HTTPException(status_code=403, detail="User is suspended")
    
    profile_view = Profile_View(viwed_id=requested_profile.id, 
                                username=requested_profile.username, 
                                viwer_id=viwer_id, 
                                is_owner=(requested_profile.id == viwer_id), 
                                name=requested_profile.name, 
                                bio=requested_profile.bio, 
                                photo_url=requested_profile.photo_url, 
                                country=requested_profile.country, 
                                verified=requested_profile.verified, 
                                status=requested_profile.status,
                                is_friends=check_friendship_status(requested_profile.id, viwer_id),
                                has_sent_friendship_request=check_friendship_request_exists(requested_profile.id, viwer_id),
                                has_received_friendship_request=check_friendship_request_exists(viwer_id, requested_profile.id),
                                is_blocked=is_blocked_friendship_exists(viwer_id, requested_profile.id))
    redis.set(f"user:session:{viwer_id}:{username}", json.dumps(profile_view.model_dump()), ex=3600)
    redis.sadd(f"profile_view_cache:{username}", f"user:session:{viwer_id}:{username}")    
    return profile_view

@router.get("/{username}/friends", response_model=UserSummary)
def read_user_friends(username: Annotated[str, Path()], user: Annotated[dict, Depends(verify_token)]):
    vwer_id = user.get("id")
    requested_profile = get_user_profile_BY_USERNAME(username)
    if not requested_profile:
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile.status != "Active":
        raise HTTPException(status_code=403, detail="User is suspended")
    if requested_profile.id != vwer_id:
        raise HTTPException(status_code=403, detail="You are not authorized to view this user's friends")
    
    friends_brief = get_friends_brief(requested_profile.id)
    return friends_brief


    