from fastapi import FastAPI, WebSocket, Depends
from database.database import get_db
from music.routes import router as music_route
from chat.routes import router as chat_route
from recommendation.routes import router as recommendation_route

app = FastAPI()


def on_startup():
    app.db_connection = get_db()


# Middlewares.
app.add_event_handler("startup", on_startup)


# Routes
app.include_router(music_route, prefix="/music")
app.include_router(chat_route, prefix="/chat")
app.include_router(recommendation_route, prefix="/recm")
