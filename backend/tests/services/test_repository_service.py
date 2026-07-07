import io
import zipfile
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.repository_analysis_service import RepositoryAnalysisService
from app.models.enums import ReviewStatus
from app.models.finding import Finding
from app.models.repository import FileReview
from app.models.review import Review
from app.models.ticket import Ticket
from app.repository.file_filter import FileFilter
from app.repository.language_detector import LanguageDetector
from app.repository.repository_scanner import RepositoryScanner
from app.repository.repository_summary import RepositorySummary


def create_mock_zip(files: dict[str, str]) -> bytes:
    """Helper to create an in-memory zip file bytes."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for filepath, content in files.items():
            zip_file.writestr(filepath, content)
    return zip_buffer.getvalue()


def test_language_detector():
    assert LanguageDetector.detect_language("main.py") == "python"
    assert LanguageDetector.detect_language("src/index.tsx") == "typescript"
    assert LanguageDetector.detect_language("index.js") == "javascript"
    assert LanguageDetector.detect_language("server.go") == "go"
    assert LanguageDetector.detect_language("App.java") == "java"
    assert LanguageDetector.detect_language("main.cpp") == "cpp"
    assert LanguageDetector.detect_language("main.cs") == "csharp"
    assert LanguageDetector.detect_language("main.txt") is None


def test_file_filter():
    assert FileFilter.is_excluded("node_modules/lodash/index.js") is True
    assert FileFilter.is_excluded(".git/config") is True
    assert FileFilter.is_excluded("src/main.py") is False
    assert FileFilter.is_binary(b"hello\x00world") is True
    assert FileFilter.is_binary(b"hello world") is False


def test_repository_scanner_success():
    files = {
        "src/main.py": "print('hello')",
        "src/utils.js": "console.log('test')",
        "node_modules/lodash/index.js": "ignored",
        "README.md": "ignored extension",
    }
    zip_bytes = create_mock_zip(files)
    scanned = RepositoryScanner.scan_zip(zip_bytes)

    assert len(scanned) == 2
    paths = [s["path"] for s in scanned]
    assert "src/main.py" in paths
    assert "src/utils.js" in paths

    # Check language matching
    main_py = next(s for s in scanned if s["path"] == "src/main.py")
    assert main_py["language"] == "python"
    assert main_py["content"] == "print('hello')"


def test_repository_scanner_validation():
    # Empty zip file
    zip_bytes = create_mock_zip({})
    with pytest.raises(ValueError, match="Uploaded ZIP archive is empty"):
        RepositoryScanner.scan_zip(zip_bytes)

    # Individual file size exceeds limit (we mock info.file_size in scanner test or just use mock)
    # Since limits are hardcoded, we can verify zip size checks
    huge_bytes = b"0" * (50 * 1024 * 1024 + 1)
    with pytest.raises(ValueError, match="exceeds the maximum limit"):
        RepositoryScanner.scan_zip(huge_bytes)


def test_repository_summary_aggregation():
    # Construct transient database-like models
    finding1 = Finding(severity="critical", ticket=Ticket(title="Fix AST"))
    finding2 = Finding(severity="medium", ticket=None)
    finding3 = Finding(severity="low", ticket=None)

    review1 = Review(language="python", status="COMPLETED", findings=[finding1, finding2])
    review2 = Review(language="javascript", status="COMPLETED", findings=[finding3])
    review3 = Review(language="python", status="PENDING", findings=[])

    fr1 = FileReview(file_path="src/main.py", size_bytes=100, review=review1)
    fr2 = FileReview(file_path="src/index.js", size_bytes=500, review=review2)
    fr3 = FileReview(file_path="src/todo.py", size_bytes=50, review=review3)

    summary = RepositorySummary.aggregate([fr1, fr2, fr3])

    assert summary["language_summary"] == {"python": 2, "javascript": 1}
    # average completed reviews quality score: (70 + 95) / 2 = 82.5 -> rounded to 82
    assert summary["overall_quality"] == 82
    assert summary["metrics"]["files_analyzed"] == 3
    assert summary["metrics"]["critical_findings"] == 1
    assert summary["metrics"]["open_tickets"] == 1

    # check largest files
    assert summary["metrics"]["largest_files"][0]["file_path"] == "src/index.js"
    assert summary["metrics"]["largest_files"][0]["size_bytes"] == 500


@pytest.mark.asyncio
async def test_repository_submit():
    # Setup mocks
    db = MagicMock(spec=AsyncSession)
    bg_tasks = MagicMock()

    from datetime import UTC, datetime
    def add_side_effect(obj):
        if hasattr(obj, 'id') and obj.id is None:
            obj.id = 1
        if hasattr(obj, 'created_at') and obj.created_at is None:
            obj.created_at = datetime.now(UTC)

    db.add.side_effect = add_side_effect

    files = {"main.py": "print('ok')"}
    zip_bytes = create_mock_zip(files)

    service = RepositoryAnalysisService()

    response = await service.submit_repository(
        db,
        name="test_repo.zip",
        file_bytes=zip_bytes,
        background_tasks=bg_tasks
    )

    assert response.status == ReviewStatus.PENDING
    db.add.assert_called()
    bg_tasks.add_task.assert_called_once()
