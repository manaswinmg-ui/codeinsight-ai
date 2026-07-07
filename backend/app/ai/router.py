import json
import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.ai.providers.base import AIProvider, AIError
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.retrieval import repository_retrieval_service
from app.ai.token_optimizer import TokenOptimizer
from app.ai.cost_logger import CostLogger

logger = logging.getLogger("app.ai.router")


def get_ai_provider() -> AIProvider:
    """Factory to get configured or fallback AI provider."""
    # Use Mock provider in non-prod when keys are empty/unset or mock is explicitly set
    if settings.ENV != "production" and (not settings.OPENAI_API_KEY or settings.AI_PROVIDER == "mock"):
        return MockAIProvider()
    return OpenAIProvider()


class AIRouter:
    def __init__(self, provider: AIProvider | None = None) -> None:
        self.provider = provider or get_ai_provider()

    @staticmethod
    def _is_high_complexity(query: str) -> tuple[bool, str]:
        """Classify if a query requires deep reasoning/escalation on entry."""
        q_lower = query.lower()
        
        # Keyword checks
        sec_keywords = {"security", "audit", "vulnerability", "penetration", "owasp"}
        arch_keywords = {"architecture", "system design", "infrastructure", "dependency tracing", "multi-file"}
        debug_keywords = {"complex debug", "memory leak", "race condition", "deadlock"}

        if any(kw in q_lower for kw in sec_keywords):
            return True, "Security audit classification"
        if any(kw in q_lower for kw in arch_keywords):
            return True, "Architecture / system design classification"
        if any(kw in q_lower for kw in debug_keywords):
            return True, "Complex debugging classification"
        
        return False, "Simple query classification"

    @staticmethod
    def _contains_insufficient_context_flags(response_text: str) -> bool:
        """Check if the LLM response indicates it needs more context."""
        flags = [
            "insufficient context",
            "need more files",
            "not enough information",
            "cannot determine without",
            "missing files",
            "don't have access to",
        ]
        return any(flag in response_text.lower() for flag in flags)

    @staticmethod
    def _extract_confidence(response_text: str) -> int | None:
        """Try to extract a confidence score from JSON outputs if present."""
        try:
            data = json.loads(response_text)
            if isinstance(data, dict):
                score = data.get("confidence") or data.get("confidence_score")
                if score is not None:
                    return int(score)
        except Exception:
            # Fallback if response is not JSON
            pass
        return None

    async def query_repository(
        self,
        db: AsyncSession,
        repository_id: int,
        query: str,
        system_prompt: str = "You are a helpful software engineering assistant.",
    ) -> dict:
        """
        Execute RAG and run the query against the routing/escalation layer.
        Returns a dict with response content and execution metrics.
        """
        start_time = time.perf_counter()
        
        # 1. Retrieve context
        logger.info(f"Retrieving context for repo {repository_id} and query: '{query[:40]}'")
        matched_chunks = await repository_retrieval_service.retrieve_context(
            db, repository_id, query, self.provider
        )

        # 2. Optimize context
        optimized_chunks = TokenOptimizer.remove_duplicate_chunks(matched_chunks)
        
        # Construct context text
        context_blocks = []
        retrieved_files = set()
        for chunk in optimized_chunks:
            path = chunk["path"]
            if not TokenOptimizer.should_ignore_file(path):
                retrieved_files.add(path)
                context_blocks.append(f"--- File: {path} ---\n{chunk['content']}\n")

        context_str = TokenOptimizer.compress_repeated_context("\n".join(context_blocks))
        
        # Compute input token estimates
        user_prompt_with_context = (
            f"Use the following retrieved project context to answer the user's question.\n\n"
            f"Context:\n{context_str}\n\n"
            f"Question: {query}"
        )
        
        input_token_estimate = self.provider.estimate_tokens(user_prompt_with_context)
        query_token_estimate = self.provider.estimate_tokens(query)

        # Determine starting routing
        primary_model = settings.OPENAI_DEFAULT_MODEL
        fallback_model = settings.OPENAI_FALLBACK_MODEL

        escalate_initially, complexity_reason = self._is_high_complexity(query)
        
        # Escalation criteria check on entry
        if input_token_estimate > settings.AI_MAX_CONTEXT_SIZE:
            escalate_initially = True
            complexity_reason = f"Context size ({input_token_estimate} tokens) exceeds primary model limit."
        elif len(retrieved_files) > settings.AI_MAX_RETRIEVED_FILES:
            escalate_initially = True
            complexity_reason = f"Number of retrieved files ({len(retrieved_files)}) exceeds primary model limit."

        selected_model = primary_model
        reason = "Routed to primary low-cost model."
        escalated = False

        response_content = ""
        output_token_estimate = 0

        # Try executing primary if not escalated initially
        if not escalate_initially:
            try:
                response_content = await self.provider.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt_with_context,
                    model=primary_model,
                    timeout=settings.AI_TIMEOUT,
                )
                output_token_estimate = self.provider.estimate_tokens(response_content)

                # Check post-generation escalation flags
                confidence = self._extract_confidence(response_content)
                
                if confidence is not None and confidence < settings.AI_ESCALATION_CONFIDENCE_THRESHOLD:
                    escalated = True
                    reason = f"Confidence score ({confidence}) below escalation threshold ({settings.AI_ESCALATION_CONFIDENCE_THRESHOLD})."
                elif self._contains_insufficient_context_flags(response_content):
                    escalated = True
                    reason = "Response flagged insufficient context keywords."

            except AIError as err:
                logger.warning(f"Primary model generation failed: {err}. Escalating to fallback.")
                escalated = True
                reason = f"Primary model failed with error: {err}"
        else:
            escalated = True
            reason = complexity_reason

        # Run fallback model if escalated
        if escalated:
            selected_model = fallback_model
            logger.info(f"Escalation triggered. Reason: {reason}. Running fallback model: {fallback_model}")
            
            # For fallback, we can supply the full query and context
            response_content = await self.provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt_with_context,
                model=fallback_model,
                timeout=settings.AI_TIMEOUT,
            )
            output_token_estimate = self.provider.estimate_tokens(response_content)

        duration = time.perf_counter() - start_time

        # Log cost transaction
        stats = CostLogger.log_transaction(
            selected_model=selected_model,
            reason_for_selection=reason,
            input_tokens=input_token_estimate,
            output_tokens=output_token_estimate,
            execution_time=duration,
            escalation_status=escalated,
            number_of_retrieved_files=len(retrieved_files),
            embedding_tokens=query_token_estimate,
        )

        return {
            "answer": response_content,
            "model_used": selected_model,
            "cost": stats["estimated_cost"],
            "escalated": escalated,
            "reason": reason,
            "files_retrieved": list(retrieved_files),
            "execution_time": duration,
        }


ai_router = AIRouter()
