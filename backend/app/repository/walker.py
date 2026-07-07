import os
from collections.abc import Generator


class RepositoryWalker:
    def __init__(self, excluded_dirs: set[str] | None = None) -> None:
        self.excluded_dirs = excluded_dirs or {
            "node_modules",
            "vendor",
            "dist",
            "build",
            ".git",
            "venv",
            ".venv",
            "__pycache__",
        }

    def walk(self, root_dir: str) -> Generator[tuple[str, str, int], None, None]:
        """
        Walks root_dir recursively.
        Yields tuples of (relative_path, absolute_path, size_bytes).
        Prunes self.excluded_dirs to prevent traversing into them.
        """
        normalized_excluded = {d.lower() for d in self.excluded_dirs}
        
        for root, dirs, files in os.walk(root_dir):
            # Prune excluded directories in-place to prevent traversal
            dirs[:] = [d for d in dirs if d.lower() not in normalized_excluded]
            
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, root_dir).replace("\\", "/")
                try:
                    size = os.path.getsize(abs_path)
                except OSError:
                    size = 0
                yield rel_path, abs_path, size
