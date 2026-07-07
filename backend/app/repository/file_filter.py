import os

from app.repository.file_descriptor import FileDescriptor
from app.repository.language_detector import LanguageDetector
from app.repository.scan_issue import ScanIssue


class FileFilter:
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
    TEMPORARY_EXTENSIONS = {".tmp", ".temp", ".bak", ".swp"}
    EXCLUDED_DIRS = {
        "node_modules",
        ".git",
        "dist",
        "build",
        "venv",
        ".venv",
        "__pycache__",
        "coverage",
        ".idea",
        ".vscode",
    }

    @classmethod
    def is_excluded(cls, file_path: str) -> bool:
        normalized_path = file_path.replace("\\", "/")
        parts = normalized_path.split("/")
        for part in parts:
            if part in cls.EXCLUDED_DIRS:
                return True
        return False

    @classmethod
    def is_binary(cls, content: bytes) -> bool:
        return b"\x00" in content

    @classmethod
    def evaluate(cls, descriptor: FileDescriptor) -> list[ScanIssue]:
        """
        Evaluates a FileDescriptor to determine its support status.
        Updates descriptor.status, descriptor.is_supported, and descriptor.language.
        Returns a list of ScanIssues discovered for this file.
        """
        issues = []
        filename = os.path.basename(descriptor.relative_path)

        # 1. Check for Hidden Files/Directories (starts with '.')
        parts = descriptor.relative_path.replace("\\", "/").split("/")
        is_hidden = any(part.startswith(".") for part in parts if part)

        if is_hidden:
            descriptor.status = "ignored"
            descriptor.is_supported = False
            issues.append(
                ScanIssue(
                    path=descriptor.relative_path, reason="Hidden File", severity="INFO"
                )
            )
            return issues

        # 2. Check for Temporary Files
        _, ext = os.path.splitext(filename.lower())
        if ext in cls.TEMPORARY_EXTENSIONS:
            descriptor.status = "ignored"
            descriptor.is_supported = False
            issues.append(
                ScanIssue(
                    path=descriptor.relative_path,
                    reason="Temporary File",
                    severity="INFO",
                )
            )
            return issues

        # 3. Check for Binary Files
        if descriptor.is_binary:
            descriptor.status = "ignored"
            descriptor.is_supported = False
            issues.append(
                ScanIssue(
                    path=descriptor.relative_path, reason="Binary File", severity="INFO"
                )
            )
            return issues

        # 4. Check for Maximum Size (e.g. 2 MB)
        if descriptor.size_bytes > cls.MAX_FILE_SIZE:
            descriptor.status = "ignored"
            descriptor.is_supported = False
            issues.append(
                ScanIssue(
                    path=descriptor.relative_path,
                    reason="File Too Large",
                    severity="WARNING",
                )
            )
            return issues

        # 5. Check for Language Support (extension mapping)
        lang = LanguageDetector.detect_language(filename)
        if not lang:
            descriptor.status = "unsupported"
            descriptor.is_supported = False
            issues.append(
                ScanIssue(
                    path=descriptor.relative_path,
                    reason="Unsupported Extension",
                    severity="INFO",
                )
            )
            return issues

        # File is supported!
        descriptor.status = "supported"
        descriptor.is_supported = True
        descriptor.language = lang
        return issues
