from pydantic import BaseModel
from app.repository.file_descriptor import FileDescriptor
from app.repository.statistics import ScanStatistics
from app.repository.scan_issue import ScanIssue


class RepositoryManifest(BaseModel):
    repository_name: str
    root_path: str
    scan_duration: float
    files: list[FileDescriptor]
    statistics: ScanStatistics
    issues: list[ScanIssue]
