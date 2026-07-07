import hashlib
import json

from app.ai.providers.base import AIProvider


class MockAIProvider(AIProvider):
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        timeout: float | None = None,
    ) -> str:
        # Return different responses to test routing and escalation paths
        p_lower = user_prompt.lower()
        if "5.5" in model:
            return f"Mock reply from {model} to question: {user_prompt[:50]}..."

        if "escalate_insufficient" in p_lower:
            return "This query has insufficient context. Please provide more files."

        if "escalate_low_confidence" in p_lower:
            return json.dumps(
                {"response": "This is a low confidence response.", "confidence": 45}
            )

        if "raise_api_error" in p_lower and "5.4" in model:
            from app.ai.providers.base import AIError

            raise AIError("Mock API error on primary model")

        # Standard review or Q&A responses
        if "eval" in p_lower:
            return json.dumps(
                {
                    "summary": "Mock audit completed.",
                    "quality_score": 80,
                    "findings": [
                        {
                            "title": "Use of eval() Detected",
                            "description": "Found eval usage",
                            "severity": "critical",
                            "category": "SECURITY",
                            "confidence": 95,
                            "line_start": 3,
                        }
                    ],
                }
            )

        return f"Mock reply from {model} to question: {user_prompt[:50]}..."

    async def embed(self, texts: list[str]) -> list[list[float]]:
        results = []
        for text in texts:
            # Generate reproducible 1536-dimensional mock vector
            hash_val = hashlib.md5(text.encode("utf-8")).hexdigest()
            seed = int(hash_val, 16) % 10000
            vector = []
            for i in range(1536):
                val = ((seed + i) * 31 % 1000) / 1000.0
                vector.append(val)

            # Normalize
            mag = sum(x * x for x in vector) ** 0.5
            norm_vector = [x / mag for x in vector] if mag > 0 else [0.0] * 1536
            results.append(norm_vector)
        return results

    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // 4)

    async def health_check(self) -> bool:
        return True
