from fastapi import APIRouter, WebSocket


router = APIRouter()
@router.websocket("/ws/{websocket_id}")
async def websocket_endpoint(websocket: WebSocket, websocket_id: int):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")