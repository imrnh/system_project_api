from fastapi import APIRouter, HTTPException, WebSocket, Depends, File, UploadFile
from music.models import MakeMusicHashModel, CreateGenreModel, CreateArtist
from database.database import get_db
import aiosqlite
from .fingerprint import FingerprintPipeline
from .search import SearchPipeline
import os


router = APIRouter()



@router.websocket("/ws/{websocket_id}")
async def websocket_endpoint(websocket: WebSocket, websocket_id: int):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


"""
    @ Generate hash of a given song and store it in the database.

    TODO:
        - Generate the hash
        - Iteratively insert every hash with certain delay to prevent crash
        - Sort the database.
 
"""


@router.post("/uploadfile/")
async def upload_file(file: UploadFile):
    try:
        if file.filename:
            filePath = os.path.join("assets/toRecognize", file.filename)
            print(filePath)
            with open(filePath, "wb") as f:
                f.write(file.file.read())
            
            search_pipeline = SearchPipeline()
            hashes = search_pipeline.serach(file.filename)

            return {"message": "File uploaded successfully", "hash": hashes}
    except Exception as e:
        print("ERROR: ---- ", e)
    return {"message": "No file received"}



@router.post("/make_hash")
async def make_hash(
    music_info: MakeMusicHashModel, db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.cursor()
    # await cursor.execute("INSERT INTO ")


""""
    @ View all the genres

"""


@router.get("/genres/")
async def get_all_genres(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.cursor()
    try:
        query = "SELECT * FROM genre;"
        await cursor.execute(query)
        all_genres = await cursor.fetchall()
        return {"tables": [(name[0], name[1]) for name in all_genres]}
    except Exception as e:
        raise {"status": 500, "error": str(e)}
    finally:
        await cursor.close()


"""
    @ View all the artists

"""


@router.get("/artist/")
async def get_all_artists(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.cursor()
    try:
        query = "SELECT * FROM artist;"
        await cursor.execute(query)
        all_genres = await cursor.fetchall()
        return {"tables": [(name[0], name[1]) for name in all_genres]}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching table names: {str(e)}"
        )
    finally:
        await cursor.close()


"""

    @ Create a new genre

"""


@router.post("/create_genre")
async def create_genre(
    genre: CreateGenreModel, db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.cursor()

    try:
        await cursor.execute("INSERT INTO genre (genre_name) VALUES (?)", (genre.name,))
        await db.commit()
        return "Succesfully create genre"
    except Exception as e:
        return {"status": 500, "error": str(e)}
    finally:
        await cursor.close()


"""
     @ Create a new artist

"""


@router.post("/create_artist")
async def create_artist(
    artist: CreateArtist, db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.cursor()

    try:
        await cursor.execute(
            "INSERT INTO artist (artist_name) VALUES (?)", (artist.name,)
        )
        await db.commit()
        return "Succesfully created artist"
    except Exception as e:
        return {"status": 500, "error": str(e)}
    finally:
        await cursor.close()


"""
    @ Generate a sample hash.
"""


@router.get("/hash/{file_name}")
def generate_hash(file_name: str):
    f_obj = FingerprintPipeline()
    hashed_codes = f_obj.fingerprint(file_name, file_path="/assets/toRecognize")

    return {"hashes": hashed_codes}
