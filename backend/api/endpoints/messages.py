from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from services.authentification import verify_token, decode_token
from asyncio import Queue
from typing import Dict
from services.messages import save_message, get_messages_between_users
from services.users import get_user_profile_BY_ID
from schemas.messages import Message
from uuid import UUID
from asyncio import Queue, gather
from services.authentification import get_ws_token
import logging
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/messages", tags=["messages_ws"])

user_queues: Dict[UUID, Queue] = {}




@router.post("/send")
async def send_message(message: Message, token: str = Depends(verify_token)):
    sender = await get_user_profile_BY_ID(message.sender_id)
    receiver = await get_user_profile_BY_ID(message.receiver_id)
    if not sender or not receiver:
        logger.warning("User not found for ID %s", message.sender_id)
        raise HTTPException(status_code=404, detail="User not found")
    if sender.status != "Active" or receiver.status != "Active":
        logger.warning("User with ID %s is not active", message.sender_id)
        raise HTTPException(status_code=403, detail="User is suspended")
    await save_message(message)
    return {"message": "Sent"}


@router.get("/between/{user1_id}/{user2_id}")
async def get_messages(user1_id: UUID, user2_id: UUID, token: str = Depends(verify_token)):
    user1 = await get_user_profile_BY_ID(user1_id)
    user2 = await get_user_profile_BY_ID(user2_id)
    if not user1 or not user2:
        logger.warning("User not found for ID %s", user1_id)
        raise HTTPException(status_code=404, detail="User not found")
    if user1.status != "Active" or user2.status != "Active":
        logger.warning("User with ID %s is not active", user1_id)
        raise HTTPException(status_code=403, detail="User is suspended")
    if str(token["id"]) not in [str(user1_id), str(user2_id)]:
        logger.warning("User with ID %s is not authorized to access messages", token["id"])
        raise HTTPException(status_code=403, detail="Forbidden")
    messages = await get_messages_between_users(user1_id, user2_id)
    return {"messages": messages}


@router.websocket("/ws/{user_id}")
async def messages_websocket(websocket: WebSocket, user_id: UUID):
    token = get_ws_token(websocket)
    if not token:
        logger.warning("Invalid or missing token for WebSocket connection")
        await websocket.close(code=1008)
        return

    try:
        user = decode_token(token)
    except Exception:
        logger.warning("Error occurred while decoding WebSocket token")
        await websocket.close(code=1008)
        return

    if str(user.get("id")) != str(user_id):
        logger.warning("User with ID %s is not authorized to connect to WebSocket", token["id"])
        await websocket.close(code=1008)
        return

    await websocket.accept()
    if user_id not in user_queues:
        user_queues[user_id] = Queue()

    async def send_loop():
        while True:
            message = await user_queues[user_id].get()
            await websocket.send_json(message)

    async def receive_loop():
        while True:
            message = await websocket.receive_json()
            receiver_id = UUID(str(message["receiver_id"]))

            if receiver_id in user_queues:
                await user_queues[receiver_id].put(message)

    try:
        await gather(send_loop(), receive_loop())
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for user with ID %s", user_id)
        if user_id in user_queues:
            del user_queues[user_id]
