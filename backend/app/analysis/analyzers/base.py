from abc import ABC, abstractmethod
from app.analysis.models import StaticFinding


class BaseAnalyzer(ABC):
    @abstractmethod
    def supports(self, language: str) -> bool:
        """Return True if the analyzer supports the given language."""
        pass

    @abstractmethod
    async def analyze(self, code: str) -> list[StaticFinding]:
        """Analyze the given code and return a list of static findings."""
        pass


class NullAnalyzer(BaseAnalyzer):
    def supports(self, language: str) -> bool:
        return False

    async def analyze(self, code: str) -> list[StaticFinding]:
        return []
