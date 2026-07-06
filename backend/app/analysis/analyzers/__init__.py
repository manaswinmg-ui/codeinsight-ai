from app.analysis.analyzers.base import BaseAnalyzer, NullAnalyzer
from app.analysis.analyzers.python_analyzer import PythonAnalyzer
from app.analysis.analyzers.javascript_analyzer import JavaScriptAnalyzer


def get_analyzer(language: str) -> BaseAnalyzer:
    """Return the static analyzer appropriate for the given language."""
    lang = str(language).lower().strip()
    if lang == "python":
        return PythonAnalyzer()
    elif lang in ("javascript", "typescript"):
        return JavaScriptAnalyzer()
    return NullAnalyzer()
