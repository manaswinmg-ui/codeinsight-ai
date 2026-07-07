import asyncio
import logging

from app.ai.client import AIClient, get_ai_client
from app.ai.prompt_builder import PromptBuilder
from app.ai.response_parser import ResponseParser, ReviewResult
from app.ai.response_validator import ResponseValidator
from app.analysis.analyzers import get_analyzer
from app.analysis.merger import FindingMerger
from app.models.review import Review

logger = logging.getLogger(__name__)


class AIReviewPipeline:
    def __init__(
        self,
        prompt_builder: PromptBuilder = PromptBuilder(),
        ai_client: AIClient = get_ai_client(),
        response_validator: ResponseValidator = ResponseValidator(),
        response_parser: ResponseParser = ResponseParser(),
        merger: FindingMerger = FindingMerger(),
    ) -> None:
        self.prompt_builder = prompt_builder
        self.ai_client = ai_client
        self.response_validator = response_validator
        self.response_parser = response_parser
        self.merger = merger

    async def process(self, review: Review) -> ReviewResult:
        """Execute full E2E hybrid pipeline logic: Static Analysis + AI Review -> Validate -> Parse -> Merge."""
        static_findings = []
        static_task = None

        try:
            analyzer = get_analyzer(review.language)
            static_task = asyncio.create_task(analyzer.analyze(review.code))
        except Exception as e:
            logger.error("Failed to initiate static analysis for language %s: %s", review.language, e)

        prompt_package = self.prompt_builder.build(review)

        if static_task:
            results = await asyncio.gather(
                static_task,
                self.ai_client.review(prompt_package),
                return_exceptions=True
            )

            static_res, raw_response = results[0], results[1]

            if isinstance(static_res, Exception):
                logger.error("Static analysis execution failed: %s", static_res)
            else:
                static_findings = static_res

            if isinstance(raw_response, Exception):
                raise raw_response
        else:
            raw_response = await self.ai_client.review(prompt_package)

        validated_response = self.response_validator.validate(raw_response)
        ai_result = self.response_parser.parse(validated_response)

        # Merge static and AI findings
        merged_findings = self.merger.merge(static_findings, ai_result.findings)

        return ReviewResult(
            summary=ai_result.summary,
            quality_score=ai_result.quality_score,
            findings=merged_findings,
        )

