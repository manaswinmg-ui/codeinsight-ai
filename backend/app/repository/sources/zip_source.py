from app.repository.sources.base import RepositorySource


class ZipRepositorySource(RepositorySource):
    def __init__(self, content: bytes, filename: str) -> None:
        self.content = content
        self.filename = filename

    def get_content(self) -> bytes:
        return self.content

    def get_filename(self) -> str:
        return self.filename
