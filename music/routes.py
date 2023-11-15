import time
from fastapi import APIRouter, HTTPException, WebSocket, Depends, File, UploadFile
from pydantic import BaseModel
from music.models import MakeMusicHashModel, CreateGenreModel, CreateArtist
from database.database import get_db
import aiosqlite
from .fingerprint import FingerprintPipeline
from .search import SearchPipeline
import os
from .crawler import MusicCrawler
from fastapi import FastAPI
from typing import List
import random
import string
from database.database import databse_engine
from pytube import YouTube

router = APIRouter()

app = FastAPI()


# @router.post("/test_db")
# async def test_db():

#     try:
#         databse_engine.execute("Create table boss(id integer,);")

#         return {"msg": "true"}
#     except Exception as e :
#         return {'err': f"{e}"}


@router.post("/uploadfile/")
async def upload_file(file: UploadFile):
    try:
        if file.filename:
            filePath = os.path.join("assets/toRecognize", file.filename)
            print(filePath)
            with open(filePath, "wb") as f:
                f.write(file.file.read())

            time.sleep(3)

            fingerprint_pipeline = FingerprintPipeline()
            hashes = fingerprint_pipeline.fingerprint(
                file.filename, "assets/toRecognize"
            )

            # os.remove("assets/toRecognize/" + file.filename)

            return {"message": "File uploaded successfully", "hash": hashes}
    except Exception as e:
        print("ERROR: ---- ", e)
    return {"message": "No file received"}


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
def generate_hash(file_name: str, file_org_name: str = "file_1.mp3"):
    f_obj = FingerprintPipeline()
    _, hashed_codes = f_obj.fingerprint(file_name, file_path="assets/downloaded")
    # _, hashed_codes_original = f_obj.fingerprint(file_org_name)

    # diff = f_obj.hash_difference(hashed_codes, hashed_codes_original)

    return {"block_count": len(hashed_codes), "hashes": hashed_codes}


@router.get("/crawl")
def download():
    sdownload_songs = MusicCrawler()
    x = sdownload_songs.songdownload()
    return {x}


def generate_unique_name(size=20):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(size))


class SongInfo(BaseModel):
    url: str
    music_title: str
    cover_img: str
    artist: List[int]
    genre: List[int]


@router.post("/download_song/")
async def download_song(
        song_info: SongInfo, db: aiosqlite.Connection = Depends(get_db)
):
    try:
        # Create the unique name for the file
        unique_name = generate_unique_name()

        # Download the YouTube video using Pytube
        yt = YouTube(song_info.url)
        video_title = yt.title
        video_stream = yt.streams.filter(only_audio=True).first()
        new_file_name = f"{unique_name}__{video_title}.mp3"
        video_stream.download(output_path="./assets/downloaded", filename=new_file_name)

        try:
            cursor = await db.cursor()
            insert_song_query = "INSERT INTO music (music_name, cover_img, music_url) VALUES (?, ?, ?)"
            db_response = await cursor.execute(
                insert_song_query,
                (
                    song_info.music_title,
                    song_info.cover_img,
                    song_info.url,
                ),
            )

            music_table_row_id = db_response.lastrowid  # fetching the id of this music in music table

            # mapping this music to its artist
            insert_music_artist_query = "INSERT INTO music_artist (music_id, artist_id) VALUES (?, ?)"
            for artist_id in song_info.artist:
                await cursor.execute(
                    insert_music_artist_query,
                    (
                        music_table_row_id,
                        artist_id,
                    ),
                )

            # mapping this music to ints genre
            insert_music_genre_query = "INSERT INTO music_genre (music_id, genre_id) VALUES (?, ?)"
            for genre_id in song_info.genre:
                await cursor.execute(
                    insert_music_genre_query,
                    (
                        music_table_row_id,
                        genre_id,
                    ),
                )

            await db.commit()  # commit all the changes if all the changes passed successfully.

            # generate fingerprint
            fingerprint_pipeline = FingerprintPipeline()
            _, fingerprints = fingerprint_pipeline.fingerprint(
                new_file_name, file_path=f"assets/downloaded"
            )



            insert_music_fingerprint_query = "INSERT INTO music_fingerprint (music_id, music_hash, time_idx) VALUES (?, ?, ?)"
            for time_idx, fingerprint in enumerate(fingerprints):
                await cursor.execute(
                    insert_music_fingerprint_query,
                    (
                        music_table_row_id,
                        fingerprint,
                        time_idx
                    ),
                )
                await db.commit()

            # remove the downloaded file. We don't need that anymore.
            # os.remove(f"assets/downloaded/{new_file_name}")

            return {"status": 200, "msg": "Music fingerprint generated successfully", "len": len(fingerprints)}

        except Exception as e:
            return {"status": 500, "msg": f"Error {e}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
