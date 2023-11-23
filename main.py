import os
from fastapi import FastAPI, UploadFile
from services.search import FingerprintPipeline
from services.crawler import crawl_songs


api = FastAPI()


@api.get("/crawle")
async def perform_crawling():
    try:
        crawl_msg = crawl_songs()
        return {"msg": f"Succesfully crawled {crawl_msg} songs"}
    except Exception as e:
        return {"msg": f"Something went wrong {e}"}


@api.post("/uploadfile/")
async def upload_file(file: UploadFile):
    try:
        if file.filename:
            filePath = os.path.join("assets/torec/", file.filename)
            with open(filePath, "wb") as f:
                f.write(file.file.read())

            fingerprint_obj = FingerprintPipeline()
            songs = fingerprint_obj.recognize(file.filename)

            return {"songs": songs}

    except Exception as e:
        print("ERROR: ---- ", e)
    return {"message": "No file received"}
