import io
import os
import shutil
import tempfile
import zipfile

from app.repository.sources.base import RepositorySource


class RepositoryExtractor:
    def __init__(self) -> None:
        self.temp_dir: str | None = None

    def __enter__(self) -> "RepositoryExtractor":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cleanup()

    def extract(self, source: RepositorySource) -> str:
        """
        Validates the ZIP archive, checks for directory traversal,
        extracts to a temp directory, and returns the path.
        """
        zip_bytes = source.get_content()
        if not zip_bytes:
            raise ValueError("Empty repository source content.")

        if not zipfile.is_zipfile(io.BytesIO(zip_bytes)):
            raise ValueError("Invalid ZIP file format.")

        self.temp_dir = tempfile.mkdtemp(prefix="codeinsight_scan_")

        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                for member in zf.infolist():
                    # Prevents Zip Slip path traversal vulnerability
                    target_path = os.path.abspath(
                        os.path.join(self.temp_dir, member.filename)
                    )
                    if not target_path.startswith(os.path.abspath(self.temp_dir)):
                        raise ValueError(
                            f"Zip Slip security vulnerability detected: {member.filename}"
                        )

                    if member.is_dir():
                        os.makedirs(target_path, exist_ok=True)
                        continue

                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with (
                        zf.open(member) as source_file,
                        open(target_path, "wb") as target_file,
                    ):
                        shutil.copyfileobj(source_file, target_file)

            return self.temp_dir
        except Exception as err:
            self.cleanup()
            raise err

    def cleanup(self) -> None:
        """Removes the temporary workspace directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = None
