from app.analysis.analyzers.base import BaseAnalyzer
from app.analysis.models import StaticFinding


class JavaScriptAnalyzer(BaseAnalyzer):
    def supports(self, language: str) -> bool:
        return language.lower() in ("javascript", "typescript")

    async def analyze(self, code: str) -> list[StaticFinding]:
        return []
