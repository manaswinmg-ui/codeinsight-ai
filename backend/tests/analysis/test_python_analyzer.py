import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.analysis.analyzers.python_analyzer import PythonAnalyzer


@pytest.mark.asyncio
async def test_python_analyzer_supports() -> None:
    analyzer = PythonAnalyzer()
    assert analyzer.supports("python") is True
    assert analyzer.supports("PYTHON") is True
    assert analyzer.supports("javascript") is False


@pytest.mark.asyncio
async def test_python_analyzer_analyze_success() -> None:
    analyzer = PythonAnalyzer()
    code = "import os\n"  # Unused import
    findings = await analyzer.analyze(code)

    assert len(findings) > 0
    f = findings[0]
    assert f.tool == "ruff"
    assert f.rule == "F401"
    assert f.severity == "high"
    assert f.category == "BEST_PRACTICE"
    assert f.line == 1
    assert "unused" in f.description.lower() or "os" in f.description.lower()


@pytest.mark.asyncio
async def test_python_analyzer_analyze_syntax_error() -> None:
    analyzer = PythonAnalyzer()
    code = "def foo(\n"  # Invalid syntax
    findings = await analyzer.analyze(code)

    assert len(findings) > 0
    f = findings[0]
    assert f.rule == "invalid-syntax"
    assert f.severity == "critical"
    assert f.category == "BUG"


@pytest.mark.asyncio
async def test_python_analyzer_timeout() -> None:
    analyzer = PythonAnalyzer()

    mock_communicate = AsyncMock(side_effect=asyncio.TimeoutError)
    mock_proc = MagicMock()
    mock_proc.communicate = mock_communicate

    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_proc)):
        findings = await analyzer.analyze("import os")
        assert findings == []
        mock_proc.kill.assert_called_once()
