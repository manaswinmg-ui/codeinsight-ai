from app.ai.response_parser import Finding
from app.analysis.merger import (
    FindingMerger,
    clean_tokens,
    is_relevant_finding,
    jaccard_similarity,
)
from app.analysis.models import StaticFinding


def test_clean_tokens_removes_stopwords() -> None:
    text = "The quick brown fox is at the code"
    tokens = clean_tokens(text)
    assert "the" not in tokens
    assert "is" not in tokens
    assert "at" not in tokens
    assert "quick" in tokens
    assert "brown" in tokens
    assert "fox" in tokens


def test_jaccard_similarity() -> None:
    s1 = {"unused", "variable", "name"}
    s2 = {"unused", "variable"}
    assert jaccard_similarity(s1, s2) == 2 / 3

    # Diff variables shouldn't match too high
    v1 = {"unused", "variable", "x"}
    v2 = {"unused", "variable", "y"}
    assert jaccard_similarity(v1, v2) == 0.5


def test_is_relevant_finding_filters_noise() -> None:
    # Noise/hallucinations should be filtered
    f_noise = Finding(
        title="No vulnerabilities found",
        description="Checked code and found nothing",
        severity="info",
    )
    assert not is_relevant_finding(f_noise)

    # Valid findings should pass
    f_valid = Finding(
        title="SQL Injection",
        description="Raw SQL parameter formatting allows injection",
        severity="critical",
    )
    assert is_relevant_finding(f_valid)

    # Low confidence should be filtered
    f_low_conf = Finding(
        title="SQL Injection",
        description="Raw SQL parameter formatting allows injection",
        severity="critical",
        confidence=30,
    )
    assert not is_relevant_finding(f_low_conf)


def test_merger_deduplicates_cleaned_tokens() -> None:
    merger = FindingMerger()
    sf = StaticFinding(
        title="Unused variable x",
        description="Variable x is declared but never used",
        severity="low",
        line=10,
        column=1,
        rule="F841",
        tool="ruff",
    )
    # Variable y on same line is NOT a duplicate (due to stop-word filtering & different token)
    ai_other_var = Finding(
        title="Unused variable y",
        description="Variable y is declared but never used",
        severity="low",
        line_start=10,
        line_end=10,
        confidence=80,
    )

    merged = merger.merge([sf], [ai_other_var])
    assert len(merged) == 2
