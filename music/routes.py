from fastapi import APIRouter, HTTPException, WebSocket, Depends, File, UploadFile
from music.models import MakeMusicHashModel, CreateGenreModel, CreateArtist
from database.database import get_db
import aiosqlite
from .fingerprint import FingerprintPipeline
from .search import SearchPipeline
import os
from .crawler import MusicCrawler
from fastapi import FastAPI
from fastapi.params import Query
from typing import List
import youtube_dl
from pydub import AudioSegment
import random
import string

router = APIRouter()

app = FastAPI()

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


@router.get("/crawl")
def download():
    sdownload_songs= MusicCrawler()
    x = sdownload_songs.songdownload()
    return {x}

def generate_unique_name(size=20):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(size))

@router.get("/download_mp3")
async def download_mp3(
    url: str = Query(..., title="YouTube URL", description="URL of the YouTube video"),
    music_band_name: str = Query(..., title="Music Band Name", description="Name of the music band"),
    genre_values: List[int] = Query(..., title="Genre Values", description="List of integer genre values separated by commas"),
):
    # Create the directory if it doesn't exist
    download_folder = "assets/downloaded"
    os.makedirs(download_folder, exist_ok=True)

    # Generate a unique name for the mp3 file
    unique_name = generate_unique_name()

    # Download the YouTube video
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{download_folder}/{unique_name}__%(title)s.%(ext)s',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = info_dict.get('title', 'unknown_title')

    # Convert the video to mp3
    mp3_file_path = f'{download_folder}/{unique_name}__{video_title}.mp3'
    audio = AudioSegment.from_file(f'{download_folder}/{unique_name}__{video_title}.webm', format='webm')
    audio.export(mp3_file_path, format='mp3')

    # Return the result in a dictionary
    result = {
        "file_name": f"{unique_name}__{video_title}.mp3",
        "artist_name": music_band_name,
        "genre_values": genre_values,
    }

    return result