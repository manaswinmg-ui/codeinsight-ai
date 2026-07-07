class LanguageDetector:
    """Detects programming language from file extensions."""

    _EXTENSION_MAP = {
        # Python
        ".py": "python",
        # JavaScript
        ".js": "javascript",
        ".jsx": "javascript",
        ".mjs": "javascript",
        ".cjs": "javascript",
        # TypeScript
        ".ts": "typescript",
        ".tsx": "typescript",
        # Go
        ".go": "go",
        # Java
        ".java": "java",
        # C++
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".h": "cpp",
        ".hpp": "cpp",
        ".hxx": "cpp",
        # C#
        ".cs": "csharp",
    }

    @classmethod
    def detect_language(cls, filename: str) -> str | None:
        """
        Return the language name for a given filename based on extension.
        Returns None if the extension is not supported.
        """
        import os

        _, ext = os.path.splitext(filename.lower())
        return cls._EXTENSION_MAP.get(ext)
