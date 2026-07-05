from datetime import UTC, datetime


def get_current_utc_time() -> datetime:
    """Helper to get current time with UTC timezone info."""
    return datetime.now(UTC)


def format_success_response(data: dict | list) -> dict:
    """Format success payloads into a standard JSON envelop."""
    return {
        "success": True,
        "data": data,
        "timestamp": get_current_utc_time().isoformat(),
    }
