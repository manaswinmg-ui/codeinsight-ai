import time
from typing import TypedDict

from pydantic import BaseModel

from app.repository.extractor import RepositoryExtractor
from app.repository.file_descriptor import FileDescriptor
from app.repository.file_filter import FileFilter
from app.repository.manifest import RepositoryManifest
from app.repository.scan_issue import ScanIssue
from app.repository.sources.base import RepositorySource
from app.repository.sources.zip_source import ZipRepositorySource
from app.repository.statistics import ScanStatistics
from app.repository.tree_builder import TreeBuilder
from app.repository.walker import RepositoryWalker


class ScannedFile(TypedDict):
    path: str
    content: str
    language: str
    size_bytes: int


class RepositoryScanResult(BaseModel):
    manifest: RepositoryManifest
    tree: str
    status: str = "COMPLETED"


class RepositoryScanner:
    """Coordinates and orchestrates the modular repository scanning pipeline."""

    MAX_ZIP_SIZE = 50 * 1024 * 1024  # 50 MB
    MAX_TOTAL_FILES = 1000
    MAX_SOURCE_FILES = 500

    @classmethod
    def scan(cls, source: RepositorySource) -> RepositoryScanResult:
        """
        Runs the complete modular scanning pipeline on the source repository.
        """
        start_time = time.perf_counter()

        # 1. Validate raw ZIP size
        zip_bytes = source.get_content()
        if len(zip_bytes) > cls.MAX_ZIP_SIZE:
            raise ValueError(
                f"ZIP archive size exceeds the maximum limit of {cls.MAX_ZIP_SIZE // (1024 * 1024)} MB."
            )

        # 2. Extract files
        extractor = RepositoryExtractor()
        temp_dir = extractor.extract(source)

        try:
            # 3. Walk directory
            walker = RepositoryWalker()
            descriptors: list[FileDescriptor] = []
            issues: list[ScanIssue] = []

            total_files_count = 0
            supported_files_count = 0

            for rel_path, abs_path, size in walker.walk(temp_dir):
                total_files_count += 1
                if total_files_count > cls.MAX_TOTAL_FILES:
                    raise ValueError(
                        f"Archive contains too many files. Maximum allowed is {cls.MAX_TOTAL_FILES}."
                    )

                # Create FileDescriptor
                descriptor = FileDescriptor.from_path(rel_path, abs_path, size)

                # Evaluate filters
                file_issues = FileFilter.evaluate(descriptor)
                issues.extend(file_issues)

                if descriptor.is_supported:
                    supported_files_count += 1
                    if supported_files_count > cls.MAX_SOURCE_FILES:
                        raise ValueError(
                            f"Archive contains too many source files. Maximum allowed is {cls.MAX_SOURCE_FILES}."
                        )

                descriptors.append(descriptor)

            if total_files_count == 0:
                raise ValueError("Uploaded ZIP archive is empty.")

            # 4. Calculate statistics
            stats = cls._build_statistics(descriptors)

            # 5. Build ASCII directory tree
            tree_dict = TreeBuilder.build_tree_dict(descriptors)
            tree_ascii = TreeBuilder.render_ascii(tree_dict)

            # 6. Build Manifest
            scan_duration = time.perf_counter() - start_time
            manifest = RepositoryManifest(
                repository_name=source.get_filename(),
                root_path=temp_dir,
                scan_duration=scan_duration,
                files=descriptors,
                statistics=stats,
                issues=issues,
            )

            return RepositoryScanResult(
                manifest=manifest,
                tree=tree_ascii,
                status="COMPLETED",
            )

        finally:
            extractor.cleanup()

    @classmethod
    def scan_zip(cls, zip_bytes: bytes) -> list[ScannedFile]:
        """
        Backwards compatible wrapper that performs the scan on zip_bytes and
        returns a list of ScannedFile dicts.
        """
        source = ZipRepositorySource(zip_bytes, "archive.zip")
        result = cls.scan(source)

        scanned_files = []
        for d in result.manifest.files:
            if d.is_supported and d.language and d.content is not None:
                scanned_files.append(
                    {
                        "path": d.relative_path,
                        "content": d.content,
                        "language": d.language,
                        "size_bytes": d.size_bytes,
                    }
                )
        return scanned_files

    @staticmethod
    def _build_statistics(descriptors: list[FileDescriptor]) -> ScanStatistics:
        total_files = len(descriptors)
        supported_files = 0
        ignored_files = 0
        unsupported_files = 0
        binary_files = 0
        largest_file = None
        total_size = 0

        language_distribution = {}

        for d in descriptors:
            total_size += d.size_bytes

            if d.status == "supported":
                supported_files += 1
                if d.language:
                    language_distribution[d.language] = (
                        language_distribution.get(d.language, 0) + 1
                    )
            elif d.status == "ignored":
                ignored_files += 1
            elif d.status == "unsupported":
                unsupported_files += 1

            if d.is_binary:
                binary_files += 1

            if largest_file is None or d.size_bytes > largest_file["size_bytes"]:
                largest_file = {"path": d.relative_path, "size_bytes": d.size_bytes}

        avg_size = (total_size / total_files) if total_files > 0 else 0.0

        return ScanStatistics(
            total_files=total_files,
            supported_files=supported_files,
            ignored_files=ignored_files,
            unsupported_files=unsupported_files,
            binary_files=binary_files,
            largest_file=largest_file,
            average_file_size=avg_size,
            language_distribution=language_distribution,
        )
