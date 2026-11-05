
from decimal import Decimal, InvalidOperation
from typing import Any


# ============================================================
# Problem 7: Dominant Topic Share (>= 50%)
# ============================================================

def _parse_topic_share(value: Any) -> Decimal | None:
    """Parse a valid topic-share value."""

    if value is None or isinstance(value, bool):
        return None

    try:
        share = Decimal(str(value).strip())

        if not share.is_finite():
            return None

    except (InvalidOperation, ValueError, TypeError):
        return None

    if share < 0 or share > 1:
        return None

    return share


# ============================================================
# Main Validation Function
# ============================================================

def validate_problem_07(author_data: dict[str, Any]) -> dict:
    """
    Detect a dominant topic share of 50% or higher.

    Input:
        Extracted GET author response.

    Source:
        topic_share_details

    Condition:
        Maximum topic share value >= 0.50
    """

    # 1. Extract topic-share information

    topic_share_details = author_data.get("topic_share_details")

    if not isinstance(topic_share_details, list) or not topic_share_details:

        return {
            "problem_id": "P7",
            "problem_name": "Dominant Topic Share",
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": "Topic-share information is missing or empty.",
            "evidence": {
                "total_topic_count": 0,
                "dominant_topic": None,
                "dominant_topic_share": None,
            },
        }

    # 2. Extract valid topic shares

    valid_topics = []

    for topic in topic_share_details:

        if not isinstance(topic, dict):
            continue

        share = _parse_topic_share(topic.get("value"))

        if share is None:
            continue

        valid_topics.append({
            "topic_id": topic.get("topic_id"),
            "topic_name": topic.get("topic_name"),
            "value": share,
        })

    # Check whether valid topic shares are available

    if not valid_topics:

        return {
            "problem_id": "P7",
            "problem_name": "Dominant Topic Share",
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": "No valid topic-share values are available.",
            "evidence": {
                "total_topic_count": 0,
                "dominant_topic": None,
                "dominant_topic_share": None,
            },
        }

    # 3. Identify the dominant topic

    dominant_topic = max(
        valid_topics,
        key=lambda item: item["value"],
    )

    dominant_share = dominant_topic["value"]

    # 4. Determine validation result

    if dominant_share >= Decimal("0.50"):

        flag = "Y"
        reason = "Dominant Topic Share Detected"

    else:

        flag = "N"
        reason = "No Dominant Topic Share"

    # 5. Return validation result

    return {
        "problem_id": "P7",
        "problem_name": "Dominant Topic Share",
        "flag": flag,
        "evaluation_status": "Evaluated",
        "reason": reason,
        "details": (
            f"Highest topic share: "
            f"{float(dominant_share) * 100:.2f}%."
        ),
        "evidence": {
            "total_topic_count": len(valid_topics),
            "dominant_topic": {
                "topic_id": dominant_topic["topic_id"],
                "topic_name": dominant_topic["topic_name"],
            },
            "dominant_topic_share": float(dominant_share),
            "dominant_topic_share_percentage": (
                float(dominant_share) * 100
            ),
            "threshold": 0.50,
        },
    }
