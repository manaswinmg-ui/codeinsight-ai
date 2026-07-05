from app.ai.prompt_builder import PromptPackage
from app.ai.providers.base import AIClient
from app.ai.providers.openai_client import OpenAIClient
from app.config import settings


class MockAIClient(AIClient):
    async def review(self, prompt_package: PromptPackage) -> str:
        """Return a structured mock JSON response string with all enhanced fields."""
        import json

        review_data = {
            "summary": (
                "Mock analysis: The code exhibits several structural issues "
                "including missing input validation, a potential SQL injection vector, "
                "and inefficient list comprehension patterns that may degrade performance "
                "under load. Overall the quality is moderate and can be improved."
            ),
            "quality_score": 62,
            "findings": [
                {
                    "title": "Missing Input Validation",
                    "description": (
                        "The function accepts external user input without validating "
                        "or sanitizing it. Malformed or malicious input can cause "
                        "unexpected crashes or security vulnerabilities downstream."
                    ),
                    "severity": "high",
                    "category": "SECURITY",
                    "confidence": 92,
                    "impact": (
                        "Unvalidated input can lead to runtime exceptions, data corruption, "
                        "or exploitation of downstream systems."
                    ),
                    "why_it_matters": (
                        "Defense-in-depth requires validating all inputs at the trust boundary. "
                        "Failing to do so violates the Principle of Least Privilege and opens "
                        "attack surfaces such as injection, overflow, or unexpected state changes."
                    ),
                    "suggested_fix": "Add input validation at the function entry point using guards or a validation schema.",
                    "improved_code": (
                        "def process_input(data: str) -> str:\n"
                        "    if not data or not isinstance(data, str):\n"
                        "        raise ValueError('Input must be a non-empty string')\n"
                        "    data = data.strip()\n"
                        "    return data"
                    ),
                    "estimated_fix_time": "15 minutes",
                    "test_case_hint": "Test with None, empty string, whitespace-only, and oversized inputs.",
                    "references": [
                        "https://owasp.org/www-project-top-ten/",
                        "https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html",
                    ],
                },
                {
                    "title": "Inefficient Loop Pattern",
                    "description": (
                        "A nested loop is used where a set lookup or dictionary map "
                        "would reduce time complexity from O(n²) to O(n), significantly "
                        "improving performance for large datasets."
                    ),
                    "severity": "medium",
                    "category": "PERFORMANCE",
                    "confidence": 85,
                    "impact": (
                        "At scale (>10k items), this pattern causes noticeable latency spikes "
                        "and increased CPU usage, potentially degrading API response times."
                    ),
                    "why_it_matters": (
                        "Algorithmic complexity is a foundational concern in software engineering. "
                        "O(n²) patterns that work fine in tests often become bottlenecks in "
                        "production when data volumes grow. Choosing the right data structure "
                        "is a key skill for writing scalable code."
                    ),
                    "suggested_fix": "Replace the inner loop with a set membership check or pre-build a lookup dictionary.",
                    "improved_code": (
                        "# Before: O(n²)\n"
                        "result = [x for x in items if x in target_list]\n\n"
                        "# After: O(n)\n"
                        "target_set = set(target_list)\n"
                        "result = [x for x in items if x in target_set]"
                    ),
                    "estimated_fix_time": "10 minutes",
                    "test_case_hint": "Benchmark with 10k+ items to confirm performance improvement.",
                    "references": [
                        "https://wiki.python.org/moin/TimeComplexity",
                        "Big-O Cheat Sheet: https://www.bigocheatsheet.com/",
                    ],
                },
            ],
        }
        return json.dumps(review_data)


def get_ai_client() -> AIClient:
    """Resolve and return the configured AI Client instance based on settings."""
    # Fallback to Mock in development/testing if no API key is set
    if settings.ENV != "production" and not settings.OPENAI_API_KEY:
        return MockAIClient()

    provider = settings.AI_PROVIDER.lower().strip()
    if provider == "openai":
        return OpenAIClient()
    elif provider == "mock":
        return MockAIClient()
    else:
        raise ValueError(f"Unsupported AI Provider: {settings.AI_PROVIDER}")
