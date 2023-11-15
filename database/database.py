import aiosqlite
from types import SimpleNamespace


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# postgres
DATABASE_URL = "postgres://shqwuqqq:hWDxSDrlneafDN-4Gl5KMys6NpWhxsSU@suleiman.db.elephantsql.com/shqwuqqq"

DATABASE_URL = "postgresql://sfsfgagqq:ajkfsdfji99459349-fasd0f@hellollulu.db.elephantsql.com/sfsfgagqq"
databse_engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=databse_engine)


# sqlite
config = SimpleNamespace(path="system.db")


async def get_db():
    async with aiosqlite.connect(config.path) as db:
        yield db
