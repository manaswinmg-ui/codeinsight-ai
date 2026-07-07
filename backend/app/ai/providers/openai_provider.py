import logging
import httpx
from app.ai.providers.base import (
    AIProvider,
    AIAuthenticationError,
    AIRateLimitError,
    AITimeoutError,
    AIConnectionError,
    AIError,
)
from app.config import settings

logger = logging.getLogger("app.ai.providers.openai_provider")


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.timeout = settings.AI_TIMEOUT

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        timeout: float | None = None,
    ) -> str:
        if not self.api_key:
            raise AIAuthenticationError("OpenAI API Key is not configured")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        request_timeout = timeout or self.timeout
        try:
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    return str(data["choices"][0]["message"]["content"])

                if response.status_code in (401, 403):
                    raise AIAuthenticationError("OpenAI authentication failed")
                elif response.status_code == 429:
                    raise AIRateLimitError("OpenAI rate limit exceeded")
                else:
                    raise AIError(f"OpenAI API returned status code {response.status_code}: {response.text}")

        except httpx.TimeoutException as err:
            raise AITimeoutError("OpenAI request timed out") from err
        except httpx.RequestError as err:
            raise AIConnectionError(f"OpenAI network connection failed: {str(err)}") from err
        except Exception as err:
            if isinstance(err, (AIAuthenticationError, AIRateLimitError, AITimeoutError, AIConnectionError, AIError)):
                raise err
            raise AIError(f"Unexpected OpenAI execution exception: {str(err)}") from err

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            raise AIAuthenticationError("OpenAI API Key is not configured")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "input": texts,
            "model": settings.OPENAI_EMBEDDING_MODEL,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    json=payload,
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    return [item["embedding"] for item in data["data"]]

                if response.status_code in (401, 403):
                    raise AIAuthenticationError("OpenAI authentication failed")
                elif response.status_code == 429:
                    raise AIRateLimitError("OpenAI rate limit exceeded")
                else:
                    raise AIError(f"OpenAI API returned status code {response.status_code}: {response.text}")

        except httpx.TimeoutException as err:
            raise AITimeoutError("OpenAI request timed out") from err
        except httpx.RequestError as err:
            raise AIConnectionError(f"OpenAI network connection failed: {str(err)}") from err
        except Exception as err:
            if isinstance(err, (AIAuthenticationError, AIRateLimitError, AITimeoutError, AIConnectionError, AIError)):
                raise err
            raise AIError(f"Unexpected OpenAI embedding execution exception: {str(err)}") from err

    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // 4)

    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers=headers,
                )
                return response.status_code == 200
        except Exception:
            return False
