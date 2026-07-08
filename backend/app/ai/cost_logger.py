import logging

logger = logging.getLogger("app.ai.cost_logger")


class CostLogger:
    # Cost per token in USD
    PRICING = {
        "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
        "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
        "text-embedding-3-small": {"input": 0.02 / 1_000_000, "output": 0.0},
    }

    @classmethod
    def calculate_cost(
        cls, model: str, input_tokens: int, output_tokens: int = 0
    ) -> float:
        """Calculate the USD cost based on token counts and model pricing."""
        model_pricing = cls.PRICING.get(model.lower().strip())
        if not model_pricing:
            # Fallback default pricing if model not matching
            model_pricing = cls.PRICING["gpt-4o-mini"]

        cost = (input_tokens * model_pricing["input"]) + (
            output_tokens * model_pricing["output"]
        )
        return cost

    @classmethod
    def log_transaction(
        cls,
        selected_model: str,
        reason_for_selection: str,
        input_tokens: int,
        output_tokens: int,
        execution_time: float,
        escalation_status: bool,
        number_of_retrieved_files: int,
        embedding_tokens: int = 0,
    ) -> dict:
        """Log transaction details to logger and return structural statistics dict."""
        llm_cost = cls.calculate_cost(selected_model, input_tokens, output_tokens)
        embed_cost = cls.calculate_cost("text-embedding-3-small", embedding_tokens, 0)
        total_cost = llm_cost + embed_cost

        stats = {
            "selected_model": selected_model,
            "reason_for_selection": reason_for_selection,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": round(total_cost, 8),
            "execution_time": round(execution_time, 4),
            "escalation_status": escalation_status,
            "number_of_retrieved_files": number_of_retrieved_files,
        }

        # Log structure (Do NOT log raw source code content for security)
        logger.info(
            "AI Transaction Stats: Model=%s, Reason=%s, InTokens=%d, OutTokens=%d, "
            "Cost=$%.8f, Time=%.4fs, Escalated=%s, FilesRetrieved=%d",
            stats["selected_model"],
            stats["reason_for_selection"],
            stats["input_tokens"],
            stats["output_tokens"],
            stats["estimated_cost"],
            stats["execution_time"],
            str(stats["escalation_status"]),
            stats["number_of_retrieved_files"],
        )

        return stats
