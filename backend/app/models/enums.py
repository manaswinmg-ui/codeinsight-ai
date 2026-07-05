from enum import StrEnum


class ReviewStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class FindingStatus(StrEnum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class FindingCategory(StrEnum):
    """Engineering classification of a code review finding."""

    BUG = "BUG"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    MAINTAINABILITY = "MAINTAINABILITY"
    READABILITY = "READABILITY"
    RELIABILITY = "RELIABILITY"
    BEST_PRACTICE = "BEST_PRACTICE"
    DOCUMENTATION = "DOCUMENTATION"
    UNKNOWN = "UNKNOWN"
