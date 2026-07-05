import logging

import httpx

from app.ai.prompt_builder import PromptPackage
from app.ai.providers.base import (
    AIAuthenticationError,
    AIClient,
    AIConnectionError,
    AIError,
    AIRateLimitError,
    AITimeoutError,
)
from app.config import settings

logger = logging.getLogger("app.ai.providers.openai")


class OpenAIClient(AIClient):
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = settings.AI_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS
        self.timeout = settings.AI_TIMEOUT

    async def review(self, prompt_package: PromptPackage) -> str:
        """Send code review prompt package to OpenAI Chat completions API."""
        if not self.api_key:
            raise AIAuthenticationError("OpenAI API Key is not configured")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt_package.system_prompt},
                {"role": "user", "content": prompt_package.user_prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        logger.info(
            f"Sending review request to OpenAI model '{self.model}' "
            f"(timeout={self.timeout}s)."
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    raw_content = data["choices"][0]["message"]["content"]
                    logger.info("OpenAI request completed successfully.")
                    return str(raw_content)

                # Handle error status codes
                if response.status_code in (401, 403):
                    raise AIAuthenticationError("OpenAI authentication failed")
                elif response.status_code == 429:
                    raise AIRateLimitError("OpenAI rate limit exceeded")
                else:
                    raise AIError(
                        f"OpenAI API returned status code {response.status_code}"
                    )

        except httpx.TimeoutException as err:
            raise AITimeoutError("OpenAI request timed out") from err
        except httpx.RequestError as err:
            raise AIConnectionError(
                f"OpenAI network connection failed: {str(err)}"
            ) from err
        except Exception as err:
            if isinstance(
                err,
                (
                    AIAuthenticationError,
                    AIRateLimitError,
                    AITimeoutError,
                    AIConnectionError,
                    AIError,
                ),
            ):
                raise err
            raise AIError(f"Unexpected OpenAI execution exception: {str(err)}") from err
