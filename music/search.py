from .fingerprint import FingerprintPipeline


class SearchPipeline:
    def __init__(self) -> None:
        self.fingerprint_obj = FingerprintPipeline()

    def serach(self, filename: str):
        hashes = self.fingerprint_obj.fingerprint(
            file_name=filename
        )

        return hashes