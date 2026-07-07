from typing import Any

from pydantic import BaseModel


class ScanStatistics(BaseModel):
    total_files: int
    supported_files: int
    ignored_files: int
    unsupported_files: int
    binary_files: int
    largest_file: dict[str, Any] | None = None
    average_file_size: float
    language_distribution: dict[str, int]
