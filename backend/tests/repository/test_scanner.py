import io
import zipfile
from unittest.mock import MagicMock

import pytest

from app.repository.extractor import RepositoryExtractor
from app.repository.file_descriptor import FileDescriptor
from app.repository.file_filter import FileFilter
from app.repository.repository_scanner import RepositoryScanner
from app.repository.sources.zip_source import ZipRepositorySource
from app.repository.tree_builder import TreeBuilder
from app.repository.walker import RepositoryWalker


def create_in_memory_zip(files: dict[str, bytes]) -> bytes:
    """Helper to create a ZIP archive in memory."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filepath, data in files.items():
            zf.writestr(filepath, data)
    return buf.getvalue()


def test_repository_source():
    content = b"fakezipcontent"
    source = ZipRepositorySource(content, "test.zip")
    assert source.get_content() == content
    assert source.get_filename() == "test.zip"


def test_extractor_zip_slip():
    # ZIP with path traversal member filename
    bad_files = {"../../evil.py": b"print('hacked')"}
    zip_bytes = create_in_memory_zip(bad_files)
    source = ZipRepositorySource(zip_bytes, "evil.zip")

    extractor = RepositoryExtractor()
    with pytest.raises(ValueError, match="Zip Slip"):
        extractor.extract(source)


def test_extractor_invalid_zip():
    source = ZipRepositorySource(b"not-a-zip", "bad.zip")
    extractor = RepositoryExtractor()
    with pytest.raises(ValueError, match="Invalid ZIP"):
        extractor.extract(source)


def test_walker_exclusions(tmp_path):
    # Setup folders
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("print(1)")

    node_dir = tmp_path / "node_modules"
    node_dir.mkdir()
    (node_dir / "index.js").write_text("console.log(2)")

    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]")

    walker = RepositoryWalker()
    results = list(walker.walk(str(tmp_path)))

    # Assert exclusions were skipped
    rel_paths = [r[0] for r in results]
    assert "src/main.py" in rel_paths
    assert "node_modules/index.js" not in rel_paths
    assert ".git/config" not in rel_paths


def test_file_filter_evaluations(tmp_path):
    # Supported python
    p1 = tmp_path / "main.py"
    p1.write_text("print(1)")
    d1 = FileDescriptor.from_path("main.py", str(p1), p1.stat().st_size)
    issues1 = FileFilter.evaluate(d1)
    assert d1.status == "supported"
    assert d1.is_supported is True
    assert d1.language == "python"
    assert len(issues1) == 0

    # Hidden file
    p2 = tmp_path / ".env"
    p2.write_text("SECRET=1")
    d2 = FileDescriptor.from_path(".env", str(p2), p2.stat().st_size)
    issues2 = FileFilter.evaluate(d2)
    assert d2.status == "ignored"
    assert d2.is_supported is False
    assert len(issues2) == 1
    assert issues2[0].reason == "Hidden File"

    # Temporary file
    p3 = tmp_path / "temp.swp"
    p3.write_text("tmp")
    d3 = FileDescriptor.from_path("temp.swp", str(p3), p3.stat().st_size)
    issues3 = FileFilter.evaluate(d3)
    assert d3.status == "ignored"
    assert d3.is_supported is False
    assert len(issues3) == 1
    assert issues3[0].reason == "Temporary File"

    # Binary file
    p4 = tmp_path / "data.bin"
    p4.write_bytes(b"\x00\x01\x02\x03")
    d4 = FileDescriptor.from_path("data.bin", str(p4), p4.stat().st_size)
    issues4 = FileFilter.evaluate(d4)
    assert d4.status == "ignored"
    assert d4.is_supported is False
    assert len(issues4) == 1
    assert issues4[0].reason == "Binary File"

    # Large file
    p5 = tmp_path / "huge.py"
    p5.write_text("a" * (FileFilter.MAX_FILE_SIZE + 10))
    d5 = FileDescriptor.from_path("huge.py", str(p5), p5.stat().st_size)
    issues5 = FileFilter.evaluate(d5)
    assert d5.status == "ignored"
    assert d5.is_supported is False
    assert len(issues5) == 1
    assert issues5[0].reason == "File Too Large"

    # Unsupported extension
    p6 = tmp_path / "readme.txt"
    p6.write_text("hello")
    d6 = FileDescriptor.from_path("readme.txt", str(p6), p6.stat().st_size)
    issues6 = FileFilter.evaluate(d6)
    assert d6.status == "unsupported"
    assert d6.is_supported is False
    assert len(issues6) == 1
    assert issues6[0].reason == "Unsupported Extension"


def test_tree_builder():
    descriptors = [
        MagicMock(relative_path="src/main.py"),
        MagicMock(relative_path="src/utils/helper.py"),
        MagicMock(relative_path="README.md"),
    ]
    tree = TreeBuilder.build_tree_dict(descriptors)
    assert "src" in tree
    assert "main.py" in tree["src"]
    assert "utils" in tree["src"]
    assert "helper.py" in tree["src"]["utils"]
    assert "README.md" in tree

    ascii_render = TreeBuilder.render_ascii(tree)
    assert "├── README.md" in ascii_render
    assert "└── src" in ascii_render


def test_scanner_end_to_end():
    files = {
        "src/main.py": b"print('hello')",
        "src/utils.py": b"def help(): pass",
        "node_modules/lodash.js": b"// dummy",
        "README.md": b"# Docs",
        "temp.tmp": b"temp",
        "binary.bin": b"\x00\x01\x02",
    }
    zip_bytes = create_in_memory_zip(files)
    source = ZipRepositorySource(zip_bytes, "demo.zip")

    result = RepositoryScanner.scan(source)
    assert result.status == "COMPLETED"

    manifest = result.manifest
    assert manifest.repository_name == "demo.zip"
    assert len(manifest.files) > 0

    stats = manifest.statistics
    assert stats.total_files == 5  # Excluding node_modules directory traversal
    assert stats.supported_files == 2  # main.py, utils.py
    assert stats.ignored_files == 2  # temp.tmp, binary.bin
    assert stats.unsupported_files == 1  # README.md
    assert stats.binary_files == 1

    # Check back-compat scan_zip wrapper
    compat_files = RepositoryScanner.scan_zip(zip_bytes)
    assert len(compat_files) == 2
    assert compat_files[0]["path"] == "src/main.py"
    assert compat_files[0]["content"] == "print('hello')"
    assert compat_files[0]["language"] == "python"
