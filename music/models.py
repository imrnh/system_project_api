from typing import List
from pydantic import BaseModel


class MakeMusicHashModel(BaseModel):
    music_title: str
    artist: List[int]
    cover: str #url to cover picture
    path: str #music path
    genre: List[int]



class CreateGenreModel(BaseModel):
    name: str


class CreateArtist(BaseModel):
    name: str