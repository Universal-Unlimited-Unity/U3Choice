from services.search_engine import SearchEngine
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Annotated
from typing_extensions import TypedDict
from services.authentification import verify_token
from services.users import get_user_profile_BY_ID
from uuid import UUID
search_router = APIRouter(prefix="/search", tags=["search"])

class UserSearchResult(TypedDict):
    id: UUID
    username: str
    name: str
    photo_url: str
    
@search_router.get("/users", response_model=dict[str, list[UserSearchResult]])
async def search_users(keyword: Annotated[str, Query(min_length=1)], limit: Annotated[int, Query(ge=1, le=100)], user: Annotated[dict[str, str], Depends(verify_token)]):
    if user.get("status") != "Active":
        raise HTTPException(status_code=403, detail="Your account is suspended")
    user_id = user.get("id")
    userprofile = await get_user_profile_BY_ID(user_id)
    if not userprofile:
        raise HTTPException(status_code=404, detail="An error occurred while searching for users")
    SE = SearchEngine(keyword)
    results = await SE.SearchForUsers(limit)
    if not results:
        raise HTTPException(status_code=404, detail="No users found")
    return {"results": results}
