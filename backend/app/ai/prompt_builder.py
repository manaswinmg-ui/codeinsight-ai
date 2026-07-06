from pydantic import BaseModel, Field

from app.models.review import Review


class PromptPackage(BaseModel):
    system_prompt: str = Field(
        ...,
        description="System prompt defining the AI persona and formatting instructions",
    )
    user_prompt: str = Field(
        ..., description="User prompt containing the source code and context"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Context metadata (e.g. language, review ID)",
    )


class PromptBuilder:
    def build(self, review: Review) -> PromptPackage:
        """Construct structured system and user prompt package from a Review."""
        system_prompt = (
            "You are an expert senior software engineer and AI engineering assistant "
            "performing a thorough code review.\n"
            "Analyze the submitted code for: bugs, security vulnerabilities, performance "
            "issues, maintainability concerns, readability problems, and best practices.\n"
            "For each issue found, provide a rich, actionable, and educational finding "
            "that helps the developer understand the problem, its consequences, and how "
            "to fix it.\n"
            "Respond strictly with a single JSON object. Do not include markdown code "
            "block wraps (such as ```json) or any conversational text before or after the JSON."
        )

        user_prompt = (
            f"Review this {review.language} source code:\n"
            "-----\n"
            f"{review.code}\n"
            "-----\n\n"
            "Provide your findings in the following JSON format structure:\n"
            "{\n"
            '  "summary": "High-level summary of the code review findings.",\n'
            '  "quality_score": 85,\n'
            '  "findings": [\n'
            "    {\n"
            '      "title": "Short title describing the finding.",\n'
            '      "description": "Detailed explanation of the issue.",\n'
            '      "severity": "critical" | "high" | "medium" | "low" | "info",\n'
            '      "category": "BUG" | "SECURITY" | "PERFORMANCE" | "MAINTAINABILITY" | "READABILITY" | "RELIABILITY" | "BEST_PRACTICE" | "DOCUMENTATION" | "UNKNOWN",\n'
            '      "confidence": 85,\n'
            '      "impact": "Short description of the potential runtime or production impact.",\n'
            '      "why_it_matters": "Educational explanation of why this issue exists, which software engineering principle is violated, and possible production consequences.",\n'
            '      "suggested_fix": "Suggested replacement code or description of fix.",\n'
            '      "improved_code": "Optional concise code snippet showing an improved implementation. Do not include markdown fences.",\n'
            '      "estimated_fix_time": "5 minutes",\n'
            '      "test_case_hint": "Test case description to verify the fix.",\n'
            '      "references": ["https://owasp.org/...", "PEP 8 - Style Guide"],\n'
            '      "line_start": 12,\n'
            '      "line_end": 15\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "IMPORTANT: For each finding, include the approximate line_start and line_end "
            "numbers in the source code where the issue occurs. Use 1-based line numbering."
        )

        metadata = {
            "review_id": review.id,
            "language": review.language,
        }

        return PromptPackage(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata=metadata,
        )

