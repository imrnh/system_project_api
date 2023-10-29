import aiosqlite
from fastapi import FastAPI, WebSocket, Depends


app = FastAPI()

#database setup
async def get_db():
    async with aiosqlite.connect('database/system.db') as db:
        yield db

def on_startup():
    print("Application startup")

def on_shutdown():
    print("Application shutdown")




# Middlewares.
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)



"""
    @Routings

"""


@app.websocket("/ws/{websocket_id}")
async def websocket_endpoint(websocket: WebSocket, websocket_id: int):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.get("/recognize")
async def home():
    return {
        "song": "Hariye tomake",
    }