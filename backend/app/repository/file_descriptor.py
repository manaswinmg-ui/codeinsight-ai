import hashlib
import os
from datetime import UTC, datetime

from pydantic import BaseModel


class FileDescriptor(BaseModel):
    relative_path: str
    absolute_path: str
    extension: str
    language: str | None = None
    size_bytes: int
    is_supported: bool = False
    is_binary: bool = False
    hash: str
    last_modified: datetime
    status: str = "unsupported"  # "supported", "ignored", "unsupported"
    content: str | None = None

    @classmethod
    def from_path(
        cls, relative_path: str, absolute_path: str, size_bytes: int
    ) -> "FileDescriptor":
        _, ext = os.path.splitext(relative_path)

        # Determine last modified datetime
        try:
            mtime = os.path.getmtime(absolute_path)
            last_modified = datetime.fromtimestamp(mtime, UTC)
        except OSError:
            last_modified = datetime.now(UTC)

        # Detect binary files (heuristic check for null bytes)
        is_binary = False
        if size_bytes > 0:
            try:
                with open(absolute_path, "rb") as f:
                    chunk = f.read(1024)
                    is_binary = b"\x00" in chunk
            except OSError:
                pass

        # Calculate file hash (MD5) and decode content
        file_hash = ""
        content = None
        if size_bytes > 0 and not is_binary:
            hasher = hashlib.md5()
            try:
                with open(absolute_path, "rb") as f:
                    content_bytes = f.read()
                    hasher.update(content_bytes)
                    try:
                        content = content_bytes.decode("utf-8")
                    except UnicodeDecodeError:
                        try:
                            content = content_bytes.decode("latin-1")
                        except Exception:
                            pass
                file_hash = hasher.hexdigest()
            except OSError:
                pass

        return cls(
            relative_path=relative_path,
            absolute_path=absolute_path,
            extension=ext,
            size_bytes=size_bytes,
            is_binary=is_binary,
            hash=file_hash,
            last_modified=last_modified,
            content=content,
        )
