import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.analysis.analyzers.javascript_analyzer import JavaScriptAnalyzer


@pytest.mark.asyncio
async def test_javascript_analyzer_supports() -> None:
    analyzer = JavaScriptAnalyzer()
    assert analyzer.supports("javascript") is True
    assert analyzer.supports("typescript") is True
    assert analyzer.supports("JAVASCRIPT") is True
    assert analyzer.supports("TYPESCRIPT") is True
    assert analyzer.supports("python") is False


@pytest.mark.asyncio
async def test_javascript_analyzer_analyze_success() -> None:
    import json

    analyzer = JavaScriptAnalyzer()

    mock_stdout = json.dumps(
        [
            {
                "filePath": "temp.js",
                "messages": [
                    {
                        "ruleId": "@typescript-eslint/no-unused-vars",
                        "severity": 1,
                        "message": "'x' is assigned a value but never used.",
                        "line": 1,
                        "column": 7,
                    }
                ],
            }
        ]
    ).encode("utf-8")

    mock_proc = MagicMock()
    mock_proc.communicate = AsyncMock(return_value=(mock_stdout, b""))

    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_proc)):
        code = "const x = 1;\n"  # Unused variable
        findings = await analyzer.analyze(code)

        assert len(findings) > 0
        f = findings[0]
        assert f.tool == "eslint"
        assert f.rule == "@typescript-eslint/no-unused-vars"
        assert f.severity == "low"
        assert f.category == "BEST_PRACTICE"
        assert f.line == 1
        assert (
            "assigned a value but never used" in f.description.lower()
            or "unused" in f.description.lower()
        )


@pytest.mark.asyncio
async def test_javascript_analyzer_analyze_syntax_error() -> None:
    import json

    analyzer = JavaScriptAnalyzer()

    mock_stdout = json.dumps(
        [
            {
                "filePath": "temp.js",
                "messages": [
                    {
                        "fatal": True,
                        "severity": 2,
                        "message": "Parsing error: Unexpected token",
                        "line": 1,
                        "column": 11,
                    }
                ],
            }
        ]
    ).encode("utf-8")

    mock_proc = MagicMock()
    mock_proc.communicate = AsyncMock(return_value=(mock_stdout, b""))

    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_proc)):
        code = "const x = ;\n"  # Syntax error
        findings = await analyzer.analyze(code)

        assert len(findings) > 0
        f = findings[0]
        assert f.tool == "eslint"
        assert f.rule == "parsing-error" or f.rule == "PARSE-ERROR"
        assert f.severity == "critical"
        assert f.category == "BUG"
        assert f.line == 1


@pytest.mark.asyncio
async def test_javascript_analyzer_timeout() -> None:
    analyzer = JavaScriptAnalyzer()

    mock_communicate = AsyncMock(side_effect=asyncio.TimeoutError)
    mock_proc = MagicMock()
    mock_proc.communicate = mock_communicate

    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_proc)):
        findings = await analyzer.analyze("const x = 1;")
        assert findings == []
        mock_proc.kill.assert_called_once()
