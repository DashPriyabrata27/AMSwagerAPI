
from decimal import Decimal, InvalidOperation
from typing import Any


# ============================================================
# Problem 9: No Affiliation, Zero Impact, and High Work Count
# ============================================================

HIGH_WORK_COUNT_THRESHOLD = 100


# ============================================================
# Helper Function
# ============================================================

def _parse_count(value: Any) -> int | None:
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

    return number if number >= 0 else None


# ============================================================
# Main Validation Function
# ============================================================

def validate_problem_09(author_data: dict[str, Any]) -> dict:
    """
    Detect authors with:
        1. No institutional affiliations.
        2. Zero citations.
        3. High publication count.

    Input:
        Extracted GET author response.

    Sources:
        affiliations_details
        summary_statistics
    """

    # 1. Check institutional affiliations

    affiliations_details = author_data.get("affiliations_details")

    if affiliations_details is None:

        affiliation_status = "No Affiliation"

    elif isinstance(affiliations_details, list):

        affiliation_status = (
            "No Affiliation"
            if not affiliations_details
            else "Has Affiliation"
        )

    else:

        return {
            "problem_id": "P9",
            "problem_name": (
                "No Affiliation, Zero Impact, and High Work Count"
            ),
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": "Invalid affiliation data.",
            "evidence": {
                "affiliation_status": "Invalid",
                "works_count": None,
                "cited_by_count": None,
                "work_count_threshold": HIGH_WORK_COUNT_THRESHOLD,
            },
        }

    # 2. Extract work and citation counts

    summary_statistics = author_data.get("summary_statistics")

    if not isinstance(summary_statistics, dict):
        summary_statistics = {}

    works_count = _parse_count(
        summary_statistics.get("total_work_count")
    )

    cited_by_count = _parse_count(
        summary_statistics.get("total_cited_by_count")
    )

    if works_count is None or cited_by_count is None:

        return {
            "problem_id": "P9",
            "problem_name": (
                "No Affiliation, Zero Impact, and High Work Count"
            ),
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": (
                "Work count or citation count is missing or invalid."
            ),
            "evidence": {
                "affiliation_status": affiliation_status,
                "works_count": works_count,
                "cited_by_count": cited_by_count,
                "work_count_threshold": HIGH_WORK_COUNT_THRESHOLD,
            },
        }

    # 3. Evaluate all three conditions

    no_affiliation = (
        affiliation_status == "No Affiliation"
    )

    zero_impact = (
        cited_by_count == 0
    )

    high_work_count = (
        works_count > HIGH_WORK_COUNT_THRESHOLD
    )

    # 4. Determine final validation result

    if no_affiliation and zero_impact and high_work_count:

        flag = "Y"
        reason = (
            "No Affiliation, Zero Impact, and High Work Count"
        )

    else:

        flag = "N"
        reason = "Suspicious Conditions Not Fully Satisfied"

    # 5. Return validation result

    return {
        "problem_id": "P9",
        "problem_name": (
            "No Affiliation, Zero Impact, and High Work Count"
        ),
        "flag": flag,
        "evaluation_status": "Evaluated",
        "reason": reason,
        "details": (
            f"Affiliation status: {affiliation_status}; "
            f"Works count: {works_count}; "
            f"Citations: {cited_by_count}."
        ),
        "evidence": {
            "affiliation_status": affiliation_status,
            "no_affiliation": no_affiliation,
            "works_count": works_count,
            "cited_by_count": cited_by_count,
            "work_count_threshold": HIGH_WORK_COUNT_THRESHOLD,
            "zero_impact": zero_impact,
            "high_work_count": high_work_count,
        },
    }
