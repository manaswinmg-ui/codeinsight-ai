from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ai.cost_logger import CostLogger
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.retrieval import RepositoryRetrievalService
from app.ai.router import AIRouter
from app.ai.token_optimizer import TokenOptimizer


def test_token_optimizer_duplicates():
    files = [
        {"path": "src/main.py", "content": "print(1)"},
        {"path": "src/main.py", "content": "print(2)"},
        {"path": "src/utils.py", "content": "print(3)"},
    ]
    unique_files = TokenOptimizer.remove_duplicate_files(files)
    assert len(unique_files) == 2
    assert unique_files[0]["content"] == "print(1)"
    assert unique_files[1]["path"] == "src/utils.py"

    chunks = [
        {"content": "duplicate content"},
        {"content": "duplicate content"},
        {"content": "unique content"},
    ]
    unique_chunks = TokenOptimizer.remove_duplicate_chunks(chunks)
    assert len(unique_chunks) == 2


def test_token_optimizer_compress():
    raw_text = "line1\n\n\n\nline2    with    spaces"
    compressed = TokenOptimizer.compress_repeated_context(raw_text)
    assert compressed == "line1\n\nline2 with spaces"


def test_token_optimizer_should_ignore():
    assert TokenOptimizer.should_ignore_file("node_modules/express/index.js") is True
    assert TokenOptimizer.should_ignore_file("src/main.py") is False
    assert TokenOptimizer.should_ignore_file("package-lock.json") is True
    assert (
        TokenOptimizer.should_ignore_file("package-lock.json", allow_lock_files=True)
        is False
    )
    assert TokenOptimizer.should_ignore_file("build/main.o") is True


def test_cost_logger_calculation():
    # Primary: $0.15/1M in, $0.60/1M out
    cost = CostLogger.calculate_cost("gpt-4o-mini", 1_000_000, 1_000_000)
    assert abs(cost - 0.75) < 1e-9

    # Fallback: $2.50/1M in, $10.00/1M out
    fallback_cost = CostLogger.calculate_cost("gpt-4o", 1_000_000, 1_000_000)
    assert abs(fallback_cost - 12.50) < 1e-9


def test_retrieval_chunking_and_similarity():
    svc = RepositoryRetrievalService(chunk_size=10, chunk_overlap=2)
    chunks = svc.chunk_text("abcdefghijkl")
    assert len(chunks) == 2
    assert chunks[0] == "abcdefghij"
    assert chunks[1] == "ijkl"

    v1 = [1.0, 0.0]
    v2 = [1.0, 0.0]
    sim = RepositoryRetrievalService.calculate_cosine_similarity(v1, v2)
    assert abs(sim - 1.0) < 1e-9

    v3 = [0.0, 1.0]
    sim_ortho = RepositoryRetrievalService.calculate_cosine_similarity(v1, v3)
    assert abs(sim_ortho - 0.0) < 1e-9


@pytest.mark.asyncio
async def test_router_normal_routing():
    mock_provider = MockAIProvider()
    router = AIRouter(provider=mock_provider)

    # Create mock session
    db = MagicMock()

    # Mock retrieval service results
    mock_chunks = [
        {"path": "src/main.py", "content": "print('hello')", "similarity": 0.8}
    ]

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "app.ai.retrieval.repository_retrieval_service.retrieve_context",
            AsyncMock(return_value=mock_chunks),
        )

        result = await router.query_repository(db, 1, "How does it work?")

        assert result["model_used"] == "gpt-4o-mini"
        assert result["escalated"] is False
        assert "gpt-4o-mini" in result["answer"]
        assert "src/main.py" in result["files_retrieved"]


@pytest.mark.asyncio
async def test_router_escalate_on_complexity():
    mock_provider = MockAIProvider()
    router = AIRouter(provider=mock_provider)
    db = MagicMock()

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "app.ai.retrieval.repository_retrieval_service.retrieve_context",
            AsyncMock(return_value=[]),
        )

        # Query with security audit keyword triggers immediate escalation
        result = await router.query_repository(
            db, 1, "Run a security audit on this project."
        )

        assert result["model_used"] == "gpt-4o"
        assert result["escalated"] is True
        assert "gpt-4o" in result["answer"]
        assert "Security audit" in result["reason"]


@pytest.mark.asyncio
async def test_router_escalate_on_insufficient_context():
    mock_provider = MockAIProvider()
    router = AIRouter(provider=mock_provider)
    db = MagicMock()

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "app.ai.retrieval.repository_retrieval_service.retrieve_context",
            AsyncMock(return_value=[]),
        )

        # "escalate_insufficient" is mocked to return insufficient context phrase
        result = await router.query_repository(db, 1, "escalate_insufficient")

        assert result["model_used"] == "gpt-4o"
        assert result["escalated"] is True
        assert "gpt-4o" in result["answer"]
        assert "insufficient context" in result["reason"]


@pytest.mark.asyncio
async def test_router_escalate_on_low_confidence():
    mock_provider = MockAIProvider()
    router = AIRouter(provider=mock_provider)
    db = MagicMock()

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "app.ai.retrieval.repository_retrieval_service.retrieve_context",
            AsyncMock(return_value=[]),
        )

        # "escalate_low_confidence" is mocked to return a JSON with confidence = 45
        result = await router.query_repository(db, 1, "escalate_low_confidence")

        assert result["model_used"] == "gpt-4o"
        assert result["escalated"] is True
        assert "gpt-4o" in result["answer"]
        assert "Confidence score" in result["reason"]


@pytest.mark.asyncio
async def test_router_escalate_on_primary_failure():
    mock_provider = MockAIProvider()
    router = AIRouter(provider=mock_provider)
    db = MagicMock()

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "app.ai.retrieval.repository_retrieval_service.retrieve_context",
            AsyncMock(return_value=[]),
        )

        # "raise_api_error" is mocked to raise AIError on primary model
        result = await router.query_repository(db, 1, "raise_api_error")

        assert result["model_used"] == "gpt-4o"
        assert result["escalated"] is True
        assert "gpt-4o" in result["answer"]
        assert "failed with error" in result["reason"]
