from fastapi import APIRouter, HTTPException
from backend.services.users import get_user_profile
from backend.schemas.users_schema import User_Profile
from backend.redis import redis
import json
router = APIRouter()

@router.get("/users/{id}", response_model=User_Profile)
def read_user_profile(id: str):
    if redis.exists(f"user:session:{id}"):
        user = json.loads(redis.get(f"user:session:{id}"))
        return user
    user = get_user_profile(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.status != "Active":
        raise HTTPException(status_code=403, detail="User is suspended")
    redis.set(f"user:session:{id}", json.dumps(user.model_dump()), ex=3600)
    return user
    