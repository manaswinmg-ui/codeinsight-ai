from typing import Any

from app.models.repository import FileReview
from app.repositories.review_query_repository import compute_quality_score


class RepositorySummary:
    """Aggregates file-level review findings and statistics into repository-level metrics."""

    @classmethod
    def aggregate(cls, file_reviews: list[FileReview]) -> dict[str, Any]:
        """
        Compute repository aggregates from a list of FileReview database model records
        (which must have review and findings preloaded).
        """
        # Overall language distribution
        language_summary: dict[str, int] = {}

        # Lists for largest and most problematic files
        largest_files_list: list[dict] = []
        problematic_files_list: list[dict] = []

        total_files = len(file_reviews)
        completed_files = 0
        total_quality_score = 0
        critical_findings = 0
        open_tickets = 0

        for fr in file_reviews:
            review = fr.review
            if not review:
                continue

            # 1. Update language counts
            lang = review.language.lower()
            language_summary[lang] = language_summary.get(lang, 0) + 1

            # 2. Extract size
            size_bytes = fr.size_bytes or 0
            largest_files_list.append(
                {"file_path": fr.file_path, "size_bytes": size_bytes}
            )

            # 3. Process findings and quality score
            findings = review.findings or []
            findings_count = len(findings)

            # Count critical findings
            for f in findings:
                if f.severity.lower() == "critical":
                    critical_findings += 1
                if f.ticket:
                    open_tickets += 1

            if review.status == "COMPLETED":
                completed_files += 1
                quality_score = compute_quality_score(findings)
                total_quality_score += quality_score
            else:
                quality_score = 0

            # If there are findings, add to candidate problematic files
            if findings_count > 0:
                problematic_files_list.append(
                    {
                        "file_path": fr.file_path,
                        "findings_count": findings_count,
                        "quality_score": quality_score,
                    }
                )

        # Calculate averages
        overall_quality = 100
        if completed_files > 0:
            overall_quality = int(round(total_quality_score / completed_files))

        # Sort largest files (top 5)
        largest_files_list.sort(key=lambda x: x["size_bytes"], reverse=True)
        largest_files = largest_files_list[:5]

        # Sort most problematic files (top 5 by findings_count descending)
        problematic_files_list.sort(key=lambda x: x["findings_count"], reverse=True)
        most_problematic_files = problematic_files_list[:5]

        # Compute a dynamic textual summary based on overall metrics
        if total_files == 0:
            summary_text = "No source files were found to analyze."
        else:
            summary_text = (
                f"Repository analysis completed. Analyzed {total_files} source file(s) "
                f"across {len(language_summary)} language(s). Overall repository quality score "
                f"is {overall_quality}/100 with {critical_findings} critical finding(s) detected."
            )

        return {
            "language_summary": language_summary,
            "overall_quality": overall_quality,
            "summary": summary_text,
            "metrics": {
                "files_analyzed": total_files,
                "critical_findings": critical_findings,
                "open_tickets": open_tickets,
                "largest_files": largest_files,
                "most_problematic_files": most_problematic_files,
            },
        }
