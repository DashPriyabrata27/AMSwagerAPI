
from decimal import Decimal, InvalidOperation
from typing import Any


# ============================================================
# Problem 6: Empty Topics With Multiple Works
# ============================================================

def _parse_work_count(value: Any) -> int | None:
    """Parse a valid non-negative integer count."""

    if value is None or isinstance(value, bool):
        return None

    try:
        number = Decimal(str(value).strip())

        if not number.is_finite():
            return None

        if number != number.to_integral_value():
            return None

        number = int(number)

    except (InvalidOperation, ValueError, TypeError):
        return None

    if number < 0:
        return None

    return number


# ============================================================
# Main Validation Function
# ============================================================

def validate_problem_06(author_data: dict[str, Any]) -> dict:
    """
    Detect authors with multiple works but no associated topics.

    Condition:
        total_topic_count == 0 AND work_count > 1

    Input:
        Extracted GET author response.

    Sources:
        topic_details -> topic_count
        summary_statistics -> total_work_count
    """

    # 1. Extract topic information

    topic_details = author_data.get("topic_details")

    if not isinstance(topic_details, dict):

        return {
            "problem_id": "P6",
            "problem_name": "Empty Topics With Multiple Works",
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": "Topic information is missing or invalid.",
            "evidence": {
                "total_topic_count": None,
                "work_count": None,
            },
        }

    total_topic_count = _parse_work_count(
        topic_details.get("topic_count")
    )

    if total_topic_count is None:

        return {
            "problem_id": "P6",
            "problem_name": "Empty Topics With Multiple Works",
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": "Topic count is missing or invalid.",
            "evidence": {
                "total_topic_count": None,
                "work_count": None,
            },
        }

    # 2. Extract total work count

    summary_statistics = author_data.get("summary_statistics")

    if not isinstance(summary_statistics, dict):
        summary_statistics = {}

    work_count = _parse_work_count(
        summary_statistics.get("total_work_count")
    )

    if work_count is None:

        return {
            "problem_id": "P6",
            "problem_name": "Empty Topics With Multiple Works",
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": "Total work count is missing or invalid.",
            "evidence": {
                "total_topic_count": total_topic_count,
                "work_count": None,
            },
        }

    # 3. Determine validation result

    if total_topic_count == 0 and work_count > 1:

        flag = "Y"
        reason = "Empty Topics With Multiple Works"

    else:

        flag = "N"
        reason = "No Empty Topics With Multiple Works"

    # 4. Return validation result

    return {
        "problem_id": "P6",
        "problem_name": "Empty Topics With Multiple Works",
        "flag": flag,
        "evaluation_status": "Evaluated",
        "reason": reason,
        "details": (
            f"Total topics: {total_topic_count}; "
            f"Total works: {work_count}."
        ),
        "evidence": {
            "total_topic_count": total_topic_count,
            "work_count": work_count,
        },
    }
