import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import get_ai_client
from app.models.review import Review
from app.repositories.review import review_repository
from app.schemas.review import SUPPORTED_LANGUAGES

logger = logging.getLogger("app.services.review")


def detect_language(code: str, language: str | None = None) -> str:  # noqa: C901
    """Detect language based on user selection or lightweight code heuristics."""
    if language:
        lang_clean = language.lower().strip()
        if lang_clean in SUPPORTED_LANGUAGES:
            return lang_clean

    # Simple heuristic fallback rules
    code_stripped = code.strip()
    if code_stripped.startswith("def ") or "import os" in code or "import sys" in code:
        return "python"
    if (
        "const " in code
        or "let " in code
        or "function " in code
        or "import React" in code
    ):
        if "interface " in code or "type " in code:
            return "typescript"
        return "javascript"
    if "package main" in code or "func main(" in code:
        return "go"
    if "public class " in code or "System.out.println" in code:
        return "java"
    if "#include <iostream>" in code or "#include <stdio.h>" in code:
        return "cpp"
    if "<html" in code or "<div" in code:
        return "html"
    if "body {" in code or ".class {" in code:
        return "css"

    # Default fallback
    return "python"


class PromptBuilder:
    @staticmethod
    def build_system_prompt() -> str:
        return (
            "You are a Senior AI Code Reviewer. Analyze the provided source code for "
            "quality, security vulnerabilities, bugs, and performance optimization. "
            "You MUST respond ONLY with a raw, valid JSON object matching the "
            "following structure. Do not wrap your output in markdown codeblocks "
            "(e.g. ```json). Just output the raw JSON.\n\n"
            "JSON structure:\n"
            "{\n"
            '  "summary": "High-level summary of code quality and issues found.",\n'
            '  "quality_score": 85,\n'
            '  "findings": [\n'
            "    {\n"
            '      "severity": "high" | "medium" | "low",\n'
            '      "description": "Detailed explanation of the issue.",\n'
            '      "suggested_fix": "Code snippet representing corrected code.",\n'
            '      "suggested_test_cases": ["scenario 1", "scenario 2"]\n'
            "    }\n"
            "  ]\n"
            "}"
        )

    @staticmethod
    def build_user_prompt(code: str, language: str) -> str:
        return f"Please review this {language} code:\n\n{code}"


class ResponseParser:
    @staticmethod
    def parse_and_validate(raw_text: str) -> dict:  # noqa: C901
        """Parse raw AI output text and normalize into standard review format."""
        # Clean any markdown wraps if the model returned them
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {raw_text}")
            raise ValueError(f"AI response is not valid JSON: {str(e)}") from e

        # Validate required fields
        if not isinstance(parsed, dict):
            raise ValueError("Parsed AI response is not a JSON object")

        if "summary" not in parsed or not isinstance(parsed["summary"], str):
            raise ValueError("AI response is missing a valid 'summary' string")

        if "quality_score" not in parsed or not isinstance(
            parsed["quality_score"], (int, float)
        ):
            raise ValueError("AI response is missing a valid 'quality_score' number")

        # Force quality score to be integer
        parsed["quality_score"] = int(parsed["quality_score"])

        # Validate findings
        if "findings" not in parsed or not isinstance(parsed["findings"], list):
            raise ValueError("AI response is missing a valid 'findings' list")

        normalized_findings = []
        for index, finding in enumerate(parsed["findings"]):
            if not isinstance(finding, dict):
                raise ValueError(f"Finding at index {index} is not an object")

            # Check and default fields
            severity = finding.get("severity", "medium")
            if severity not in ["high", "medium", "low"]:
                severity = "medium"

            description = finding.get("description")
            if not description or not isinstance(description, str):
                raise ValueError(
                    f"Finding at index {index} is missing a valid description"
                )

            suggested_fix = finding.get("suggested_fix")
            if not suggested_fix or not isinstance(suggested_fix, str):
                suggested_fix = ""

            test_cases = finding.get("suggested_test_cases", [])
            if not isinstance(test_cases, list):
                test_cases = []
            test_cases = [str(tc) for tc in test_cases]

            normalized_findings.append(
                {
                    "severity": severity,
                    "description": description,
                    "suggested_fix": suggested_fix,
                    "suggested_test_cases": test_cases,
                }
            )

        parsed["findings"] = normalized_findings
        return parsed


class ReviewService:
    def __init__(self):
        self.ai_client = get_ai_client()
        self.repository = review_repository

    async def create_review(
        self,
        db: AsyncSession,
        code: str,
        language: str | None = None,
        user_id: int | None = None,
    ) -> Review:
        """Run E2E code review: detect language, prompt AI, parse and persist."""
        resolved_lang = detect_language(code, language)

        system_prompt = PromptBuilder.build_system_prompt()
        user_prompt = PromptBuilder.build_user_prompt(code, resolved_lang)
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"

        # Call AI Provider client
        try:
            raw_response = await self.ai_client.analyze_code(
                combined_prompt, resolved_lang
            )
        except Exception as e:
            logger.error(f"AI Client analysis failed: {str(e)}")
            raise e

        # Parse & Validate Output structure
        parsed_payload = ResponseParser.parse_and_validate(raw_response)

        # Build Review object data
        review_record = await self.repository.create_review(
            db,
            code=code,
            language=resolved_lang,
            summary=parsed_payload["summary"],
            raw_response=parsed_payload,
            user_id=user_id,
        )

        return review_record


review_service = ReviewService()
