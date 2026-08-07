from fastapi import APIRouter, HTTPException, Depends, Path, Body
from U3Choice.backend.services.users import get_user_profile_BY_ID
from schemas.friendships_schema import Friendships, Friendships_short, blocked_friendships, blocked_friendships_short
from services.friendships import check_friendship_request_exists, send_friendship_request, accept_friendship_request, reject_friendship_request, block_friendship, unblock_friendship
from exceptions import FriendRequestNotFound, FriendshipAlreadyBlocked, FriendshipNotBlocked, SelfBlockError
from typing import Annotated
from services.authentification import verify_token
from services.friendships import check_friendship_status, check_friendship_request_exists, is_blocked_friendship_exists, remove_friendship

router = APIRouter(prefix="/friendships", tags=["friendships"])


@router.post("/send_request")
async def send_request(friendship: Annotated[Friendships, Body()], user: Annotated[dict, Depends(verify_token)]):
    if friendship.sender_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to send a friendship request for this user")
    if friendship.sender_id == friendship.receiver_id:
        raise HTTPException(status_code=400, detail="You cannot send a friendship request to yourself")
    if await check_friendship_request_exists(friendship.sender_id, friendship.receiver_id):
        raise HTTPException(status_code=400, detail="Friendship request already exists")
    requested_profile1 = await get_user_profile_BY_ID(friendship.receiver_id)
    requested_profile2 = await get_user_profile_BY_ID(friendship.sender_id)
    if not requested_profile1 or not requested_profile2:
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile1.status != "Active" or requested_profile2.status != "Active":
        raise HTTPException(status_code=403, detail="One or both users are suspended")
    await send_friendship_request(friendship)
    return {"message": "Friendship request sent successfully"}

@router.post("/accept_request")
async def accept_request(friendship: Annotated[Friendships_short, Body()], user: Annotated[dict, Depends(verify_token)]):
    if friendship.receiver_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to accept a friendship request for this user")
    requested_profile1 = await get_user_profile_BY_ID(friendship.receiver_id)
    requested_profile2 = await get_user_profile_BY_ID(friendship.sender_id)
    if not requested_profile1 or not requested_profile2:
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile1.status != "Active" or requested_profile2.status != "Active":
        raise HTTPException(status_code=403, detail="One or both users are suspended")
    try:
        await accept_friendship_request(friendship.sender_id, friendship.receiver_id)
        return {"message": "Friendship request accepted successfully"}
    except FriendRequestNotFound:
        raise HTTPException(status_code=404, detail="Friendship request not found")

@router.post("/reject_request")
async def reject_request(friendship: Annotated[Friendships_short, Body()], user: Annotated[dict, Depends(verify_token)]):
    if friendship.receiver_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to reject a friendship request for this user")
    if friendship.sender_id == friendship.receiver_id:
        raise HTTPException(status_code=400, detail="You cannot reject a friendship request from yourself")
    if not await check_friendship_request_exists(friendship.sender_id, friendship.receiver_id):
        raise HTTPException(status_code=404, detail="Friendship request does not exist")
    requested_profile1 = await get_user_profile_BY_ID(friendship.receiver_id)
    requested_profile2 = await get_user_profile_BY_ID(friendship.sender_id)
    if not requested_profile1 or not requested_profile2:
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile1.status != "Active" or requested_profile2.status != "Active":
        raise HTTPException(status_code=403, detail="One or both users are suspended")
    try:
        await reject_friendship_request(friendship.sender_id, friendship.receiver_id)
        return {"message": "Friendship request rejected successfully"}
    except FriendRequestNotFound:
        raise HTTPException(status_code=404, detail="Friendship request not found")

@router.delete("/remove_friendship")
async def remove_friendship(friendship: Annotated[Friendships_short, Body()], user: Annotated[dict, Depends(verify_token)]):
@router.post("/block")
async def block_friendship_endpoint(blocked: Annotated[blocked_friendships, Body()], user: Annotated[dict, Depends(verify_token)]):
    if blocked.blocker_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to block this user")
    requested_profile1 = await get_user_profile_BY_ID(blocked.blocker_id)
    requested_profile2 = await get_user_profile_BY_ID(blocked.blocked_id)
    if not requested_profile1 or not requested_profile2:
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile1.status != "Active" or requested_profile2.status != "Active":
        raise HTTPException(status_code=403, detail="One or both users are suspended")
    try:
        await block_friendship(blocked.blocker_id, blocked.blocked_id)
        return {"message": "User blocked successfully"}
    except SelfBlockError:
        raise HTTPException(status_code=400, detail="You cannot block yourself")
    except FriendshipAlreadyBlocked:
        raise HTTPException(status_code=400, detail="Friendship already blocked")

@router.post("/unblock")
async def unblock_friendship_endpoint(blocked: Annotated[blocked_friendships_short, Body()], user: Annotated[dict, Depends(verify_token)]):
    if blocked.blocker_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to unblock this user")
    requested_profile1 = await get_user_profile_BY_ID(blocked.blocker_id)
    requested_profile2 = await get_user_profile_BY_ID(blocked.blocked_id)
    if not requested_profile1 or not requested_profile2:
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile1.status != "Active" or requested_profile2.status != "Active":
        raise HTTPException(status_code=403, detail="One or both users are suspended")
    if not await is_blocked_friendship_exists(blocked.blocker_id, blocked.blocked_id):
        raise HTTPException(status_code=404, detail="Friendship not blocked")
    try:
        await unblock_friendship(blocked.blocker_id, blocked.blocked_id)
        return {"message": "User unblocked successfully"}
    except SelfBlockError:
        raise HTTPException(status_code=400, detail="You cannot unblock yourself")
    except FriendshipNotBlocked:
        raise HTTPException(status_code=404, detail="Friendship not blocked")
    
@router.delete("/remove_friendship")
async def remove_friendship_endpoint(friendship: Annotated[Friendships_short, Body()], user: Annotated[dict, Depends(verify_token)]):
    if friendship.sender_id != user.get("id") and friendship.receiver_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to remove this friendship")
    requested_profile1 = await get_user_profile_BY_ID(friendship.sender_id)
    requested_profile2 = await get_user_profile_BY_ID(friendship.receiver_id)
    if not requested_profile1 or not requested_profile2:
        raise HTTPException(status_code=404, detail="User not found")
    if requested_profile1.status != "Active" or requested_profile2.status != "Active":
        raise HTTPException(status_code=403, detail="One or both users are suspended")
    try:
        await remove_friendship(friendship.sender_id, friendship.receiver_id)
        return {"message": "Friendship removed successfully"}
    except FriendRequestNotFound:
        raise HTTPException(status_code=404, detail="Friendship does not exist")
