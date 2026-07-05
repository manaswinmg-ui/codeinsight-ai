import abc

from app.ai.prompt_builder import PromptPackage


class AIError(Exception):
    """Base class for all AI provider exceptions."""

    pass


class AIAuthenticationError(AIError):
    """Raised when provider authentication fails (e.g. invalid API key)."""

    pass


class AIRateLimitError(AIError):
    """Raised when rate limits are exceeded."""

    pass


class AITimeoutError(AIError):
    """Raised when the AI provider connection times out."""

    pass


class AIConnectionError(AIError):
    """Raised when network connection fails."""

    pass


class AIClient(abc.ABC):
    @abc.abstractmethod
    async def review(self, prompt_package: PromptPackage) -> str:
        """Send prompt package to provider and return the raw response string."""
        pass
