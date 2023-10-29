import aiosqlite
from types import SimpleNamespace


config = SimpleNamespace(path="system.db")


async def get_db():
    async with aiosqlite.connect(config.path) as db:
        yield db
