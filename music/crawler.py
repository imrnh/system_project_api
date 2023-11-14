"""
    TODO:
        # Fetch music from database.
        # Generate hash.
        # Iteratively push hash to the db.
"""
from pytube import YouTube
from .fingerprint import FingerprintPipeline


class MusicCrawler:

    def __int__(self):
        self.fingerprint_generator = FingerprintPipeline()
    
    def songdownload(self): 
        yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
        return yt.title

    def read_music(self):  # read from db.
        pass

    def make_fingerprint(self, audio_path):
        self.fingerprint_generator.fingerprint(audio_path)
