import json


class AIResponseValidationError(ValueError):
    """Raised when the AI response fails JSON validation or schema constraints."""

    pass


VALID_CATEGORIES = {
    "BUG",
    "SECURITY",
    "PERFORMANCE",
    "MAINTAINABILITY",
    "READABILITY",
    "RELIABILITY",
    "BEST_PRACTICE",
    "DOCUMENTATION",
    "UNKNOWN",
}


class ResponseValidator:
    def validate(self, raw_response: str) -> dict:
        """Sanitize and validate raw AI response text against top-level constraints."""
        cleaned = self._sanitize(raw_response)

        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError as err:
            raise AIResponseValidationError(
                f"AI response is not valid JSON: {str(err)}"
            ) from err

        if not isinstance(payload, dict):
            raise AIResponseValidationError("AI response must be a JSON object")

        self._validate_schema(payload)
        return payload

    def _sanitize(self, raw_response: str) -> str:
        """Strip markdown fences and trim whitespace."""
        if not raw_response or not raw_response.strip():
            raise AIResponseValidationError("AI response is empty")

        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            if cleaned.lower().startswith("```json"):
                cleaned = cleaned[7:]
            else:
                cleaned = cleaned[3:]

            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

        return cleaned

    def _validate_schema(self, payload: dict) -> None:
        """Verify presence and type/value bounds of required top-level keys."""
        required_keys = ["summary", "quality_score", "findings"]
        for key in required_keys:
            if key not in payload:
                raise AIResponseValidationError(
                    f"Missing required top-level key: '{key}'"
                )

        if not isinstance(payload["summary"], str):
            raise AIResponseValidationError(
                "Top-level field 'summary' must be a string"
            )

        score = payload["quality_score"]
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            raise AIResponseValidationError(
                "Top-level field 'quality_score' must be a number"
            )

        if not (0 <= score <= 100):
            raise AIResponseValidationError(
                f"Field 'quality_score' must be between 0 and 100, got {score}"
            )

        if not isinstance(payload["findings"], list):
            raise AIResponseValidationError("Top-level field 'findings' must be a list")

        # Validate optional per-finding enhanced fields
        for i, finding in enumerate(payload["findings"]):
            if not isinstance(finding, dict):
                continue
            self._validate_finding_fields(finding, index=i)

    def _validate_finding_fields(self, finding: dict, index: int) -> None:
        """Validate optional enhanced fields within a single finding dict."""
        # confidence: if present, must be numeric 0–100
        confidence = finding.get("confidence")
        if confidence is not None:
            if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
                raise AIResponseValidationError(
                    f"Finding[{index}].confidence must be a number, got {type(confidence).__name__}"
                )
            if not (0 <= confidence <= 100):
                raise AIResponseValidationError(
                    f"Finding[{index}].confidence must be 0–100, got {confidence}"
                )

        # category: if present, must be a recognized string
        category = finding.get("category")
        if category is not None:
            if not isinstance(category, str):
                raise AIResponseValidationError(
                    f"Finding[{index}].category must be a string"
                )
            normalized = str(category).strip().upper()
            if normalized not in VALID_CATEGORIES:
                # Warn but don't raise — will be normalized to UNKNOWN by parser
                pass

        # references: if present, must be a list
        references = finding.get("references")
        if references is not None and not isinstance(references, list):
            raise AIResponseValidationError(
                f"Finding[{index}].references must be a list if present"
            )
