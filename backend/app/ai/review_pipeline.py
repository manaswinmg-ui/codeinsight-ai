from app.ai.client import AIClient, get_ai_client
from app.ai.prompt_builder import PromptBuilder
from app.ai.response_parser import ResponseParser, ReviewResult
from app.ai.response_validator import ResponseValidator
from app.models.review import Review


class AIReviewPipeline:
    def __init__(
        self,
        prompt_builder: PromptBuilder = PromptBuilder(),
        ai_client: AIClient = get_ai_client(),
        response_validator: ResponseValidator = ResponseValidator(),
        response_parser: ResponseParser = ResponseParser(),
    ) -> None:
        self.prompt_builder = prompt_builder
        self.ai_client = ai_client
        self.response_validator = response_validator
        self.response_parser = response_parser

    async def process(self, review: Review) -> ReviewResult:
        """Execute full E2E AI pipeline logic: Prompt -> LLM -> Validate -> Parse."""
        prompt_package = self.prompt_builder.build(review)
        raw_response = await self.ai_client.review(prompt_package)
        validated_response = self.response_validator.validate(raw_response)
        return self.response_parser.parse(validated_response)
