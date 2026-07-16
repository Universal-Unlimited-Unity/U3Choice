from fastapi import APIRouter, HTTPException, Depends, Path, Body
from backend.schemas.friendships_schema import Friendships, Friendships_short, blocked_friendships, blocked_friendships_short
from backend.services.friendships import send_friendship_request, accept_friendship_request, reject_friendship_request, block_friendship, unblock_friendship
from backend.exceptions import FriendRequestNotFound, FriendshipAlreadyBlocked, FriendshipNotBlocked, SelfBlockError
from typing import Annotated
from backend.services.authentification import verify_token

router = APIRouter(prefix="/friendships", tags=["friendships"])


@router.post("/send_request")
def send_request(friendship: Annotated[Friendships, Body()], user: Annotated[dict, Depends(verify_token)]):
    if friendship.sender_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to send a friendship request for this user")
    send_friendship_request(friendship)
    return {"message": "Friendship request sent successfully"}

@router.post("/accept_request")
def accept_request(friendship: Annotated[Friendships_short, Body()], user: Annotated[dict, Depends(verify_token)]):
    if friendship.receiver_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to accept a friendship request for this user")
    try:
        accept_friendship_request(friendship.sender_id, friendship.receiver_id)
        return {"message": "Friendship request accepted successfully"}
    except FriendRequestNotFound:
        raise HTTPException(status_code=404, detail="Friendship request not found")

@router.post("/reject_request")
def reject_request(friendship: Annotated[Friendships_short, Body()], user: Annotated[dict, Depends(verify_token)]):
    if friendship.receiver_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to reject a friendship request for this user")
    try:
        reject_friendship_request(friendship.sender_id, friendship.receiver_id)
        return {"message": "Friendship request rejected successfully"}
    except FriendRequestNotFound:
        raise HTTPException(status_code=404, detail="Friendship request not found")

@router.post("/block")
def block_friendship_endpoint(blocked: Annotated[blocked_friendships, Body()], user: Annotated[dict, Depends(verify_token)]):
    if blocked.blocker_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to block this user")
    try:
        block_friendship(blocked.blocker_id, blocked.blocked_id)
        return {"message": "User blocked successfully"}
    except SelfBlockError:
        raise HTTPException(status_code=400, detail="You cannot block yourself")
    except FriendshipAlreadyBlocked:
        raise HTTPException(status_code=400, detail="Friendship already blocked")

@router.post("/unblock")
def unblock_friendship_endpoint(blocked: Annotated[blocked_friendships_short, Body()], user: Annotated[dict, Depends(verify_token)]):
    if blocked.blocker_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You are not authorized to unblock this user")
    try:
        unblock_friendship(blocked.blocker_id, blocked.blocked_id)
        return {"message": "User unblocked successfully"}
    except SelfBlockError:
        raise HTTPException(status_code=400, detail="You cannot unblock yourself")
    except FriendshipNotBlocked:
        raise HTTPException(status_code=404, detail="Friendship not blocked")
