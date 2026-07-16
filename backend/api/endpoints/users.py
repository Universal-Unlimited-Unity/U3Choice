from fastapi import APIRouter, HTTPException, Depends, Path, Body, Query
from backend.services.users import get_user_profile, get_user_profile_BY_USERNAME
from backend.schemas.users_schema import Profile_View
from backend.redis import redis
import json
from fastapi.security import OAuth2PasswordBearer
from backend.services.authentification import decode_token
import jwt
from typing import Annotated

router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="VerifyToken")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        user = decode_token(token)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

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
    
    profile_view = Profile_View(viwed_id=requested_profile.id, username=requested_profile.username, viwer_id=viwer_id, is_owner=(requested_profile.id == viwer_id), name=requested_profile.name, bio=requested_profile.bio, photo_url=requested_profile.photo_url, country=requested_profile.country, verified=requested_profile.verified, status=requested_profile.status)
    redis.set(f"user:session:{viwer_id}:{username}", json.dumps(profile_view.model_dump()), ex=3600)    
    return profile_view