import re


class TokenOptimizer:
    @staticmethod
    def remove_duplicate_files(files: list[dict]) -> list[dict]:
        """Remove files with duplicate paths, keeping the first occurrence."""
        seen = set()
        unique_files = []
        for f in files:
            path = f.get("path") or f.get("file_path")
            if path not in seen:
                seen.add(path)
                unique_files.append(f)
        return unique_files

    @staticmethod
    def remove_duplicate_chunks(chunks: list[dict]) -> list[dict]:
        """Remove chunks with duplicate content, keeping the first occurrence."""
        seen = set()
        unique_chunks = []
        for c in chunks:
            content = c.get("content")
            if content not in seen:
                seen.add(content)
                unique_chunks.append(c)
        return unique_chunks

    @staticmethod
    def compress_repeated_context(text: str) -> str:
        """Compress consecutive blank lines and excess whitespace in text."""
        if not text:
            return ""
        # Collapse multiple newlines (3 or more) to exactly two
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Collapse multiple spaces (2 or more) to a single space
        text = re.sub(r" {2,}", " ", text)
        return text

    @classmethod
    def should_ignore_file(cls, filename: str, allow_lock_files: bool = False) -> bool:
        """
        Check if a file should be ignored based on path segments or extensions.
        Matches binary, generated files, lock files, node_modules, and vendor folders.
        """
        normalized = filename.replace("\\", "/").lower()
        parts = normalized.split("/")

        # Excluded directories
        excluded_dirs = {
            "node_modules",
            "vendor",
            "dist",
            "build",
            ".git",
            "venv",
            ".venv",
            "__pycache__",
        }
        if any(part in excluded_dirs for part in parts):
            return True

        # Lock files (unless allowed)
        lock_files = {
            "package-lock.json",
            "yarn.lock",
            "poetry.lock",
            "cargo.lock",
            "pnpm-lock.yaml",
        }
        if not allow_lock_files and parts[-1] in lock_files:
            return True

        # Common temporary or build patterns
        import os

        _, ext = os.path.splitext(normalized)
        temp_extensions = {".tmp", ".temp", ".swp", ".bak"}
        if ext in temp_extensions:
            return True

        # Generated files
        if parts[-1].endswith(".min.js") or parts[-1].endswith(".map"):
            return True

        return False
