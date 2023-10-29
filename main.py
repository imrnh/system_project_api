import aiosqlite
from fastapi import FastAPI, WebSocket, Depends
from music.routes import routes as music_route
from chat.routes import routes as chat_route
from recommendation.routes import routes as recommendation_route

app = FastAPI()


# database setup
async def get_db():
    async with aiosqlite.connect("database/system.db") as db:
        yield db


def on_startup():
    print("Application startup")


def on_shutdown():
    print("Application shutdown")


# Middlewares.
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)

app.include_router(music_route, prefix="/music")
app.include_router(chat_route, prefix="/chat")
app.include_router(recommendation_route, prefix="/recm")





@app.get("/recognize")
async def home():
    return {
        "song": "Hariye tomake",
    }
