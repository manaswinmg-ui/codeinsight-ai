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


class AIProvider(abc.ABC):
    @abc.abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        timeout: float | None = None,
    ) -> str:
        """Generate text using a specific model."""
        pass

    @abc.abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        pass

    @abc.abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in the given text."""
        pass

    @abc.abstractmethod
    async def health_check(self) -> bool:
        """Check provider health/connection status."""
        pass
