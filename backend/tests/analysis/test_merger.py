from app.ai.response_parser import Finding
from app.analysis.merger import FindingMerger
from app.analysis.models import StaticFinding


def test_merger_static_to_finding_mapping() -> None:
    merger = FindingMerger()
    sf = StaticFinding(
        title="Ruff (F401): Unused Import",
        description="`os` imported but unused",
        severity="medium",
        line=5,
        column=8,
        rule="F401",
        tool="ruff",
        category="BEST_PRACTICE",
        confidence=100
    )
    f = merger._static_to_finding(sf)
    assert f.title == sf.title
    assert f.description == sf.description
    assert f.severity == "MEDIUM"
    assert f.line_start == 5
    assert f.line_end == 5
    assert f.references == ["ruff rule: F401"]


def test_merger_deduplicate_same_title() -> None:
    merger = FindingMerger()

    sf = StaticFinding(
        title="Unused Import",
        description="unused import os",
        severity="medium",
        line=2,
        column=1,
        rule="F401",
        tool="ruff"
    )
    ai_finding = Finding(
        title="Unused Import",
        description="Remove unused import statement for os",
        severity="low",
        line_start=2,
        line_end=2,
        confidence=80
    )

    merged = merger.merge([sf], [ai_finding])
    assert len(merged) == 1
    assert merged[0].severity == "MEDIUM"
    assert merged[0].confidence == 100


def test_merger_deduplicate_same_line_similar_description() -> None:
    merger = FindingMerger()

    sf = StaticFinding(
        title="Ruff F401",
        description="`os` is imported but never used in the module",
        severity="medium",
        line=3,
        column=1,
        rule="F401",
        tool="ruff"
    )
    ai_finding = Finding(
        title="Clean up unused import",
        description="`os` is imported but never used anywhere",
        severity="low",
        line_start=3,
        line_end=3,
        confidence=90
    )

    merged = merger.merge([sf], [ai_finding])
    assert len(merged) == 1
    assert merged[0].confidence == 100


def test_merger_no_deduplicate_different_lines() -> None:
    merger = FindingMerger()

    sf = StaticFinding(
        title="Unused Import",
        description="unused import os",
        severity="medium",
        line=2,
        column=1,
        rule="F401",
        tool="ruff"
    )
    ai_finding = Finding(
        title="Unused Import",
        description="unused import sys",
        severity="low",
        line_start=15,
        line_end=15,
        confidence=80
    )

    merged = merger.merge([sf], [ai_finding])
    assert len(merged) == 2


def test_merger_severity_sorting() -> None:
    merger = FindingMerger()

    sf1 = StaticFinding(
        title="Medium Issue",
        description="desc",
        severity="medium",
        line=2,
        column=1,
        rule="R1",
        tool="tool"
    )
    sf2 = StaticFinding(
        title="Critical Issue",
        description="desc",
        severity="critical",
        line=3,
        column=1,
        rule="R2",
        tool="tool"
    )
    ai1 = Finding(
        title="High Issue",
        description="desc",
        severity="high",
        line_start=4,
        line_end=4,
        confidence=90
    )

    merged = merger.merge([sf1, sf2], [ai1])
    assert len(merged) == 3
    assert merged[0].severity == "CRITICAL"
    assert merged[1].severity == "HIGH"
    assert merged[2].severity == "MEDIUM"


def test_merger_line_inheritance() -> None:
    merger = FindingMerger()

    sf = StaticFinding(
        title="Unused Import",
        description="unused import os",
        severity="medium",
        line=5,
        column=1,
        rule="F401",
        tool="ruff",
        confidence=50
    )
    ai = Finding(
        title="Unused Import",
        description="unused import os",
        severity="medium",
        line_start=None,
        line_end=None,
        confidence=95
    )

    merged = merger.merge([sf], [ai])
    assert len(merged) == 1
    assert merged[0].confidence == 95
    assert merged[0].line_start == 5
    assert merged[0].line_end == 5
