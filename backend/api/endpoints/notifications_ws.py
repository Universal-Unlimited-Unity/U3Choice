from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from services.authentification import decode_token, verify_token
from asyncio import Queue
from typing import Dict
from uuid import UUID
from services.notifications import get_notifications_for_user
from services.users import get_users_by_ids, get_user_profile_BY_ID
from services.authentification import get_ws_token
user_queues: Dict[UUID, Queue] = {}

router = APIRouter(prefix="/notifications", tags=["notifications_ws"])

@router.websocket("/ws/{user_id}")
async def notifications_ws(websocket: WebSocket, user_id: UUID):
    token = get_ws_token(websocket)

    if not token:
        await websocket.close(code=1008)
        return

    try:
        token = decode_token(token)
    except Exception:
        await websocket.close(code=1008)
        return

    if str(token.get("id")) != str(user_id):
        await websocket.close(code=1008)
        return

    await websocket.accept()

    if user_id not in user_queues:
        user_queues[user_id] = Queue()

    try:
        while True:
            notification = await user_queues[user_id].get()
            await websocket.send_json(notification)
    except WebSocketDisconnect:
        del user_queues[user_id]

@router.get("/{user_id}")
async def get_notifications(user_id: UUID, token: str = Depends(verify_token)):
    if str(token["id"]) != str(user_id):
        raise HTTPException(status_code=403, detail="Forbidden")
    user = await get_user_profile_BY_ID(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.status != "Active":
        raise HTTPException(status_code=403, detail="User is suspended")
    notifications = await get_notifications_for_user(user_id)
    if not notifications:
        return {"notifications": []}
    for notification in notifications:
        notification["root_user"] = (await get_user_profile_BY_ID(notification["root_id"])).model_dump(exclude={"pwd_hash"})
    return {"notifications": notifications}
        
    