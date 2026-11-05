
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any


# ============================================================
# Problem 3: Long Work Span (> 80 Years)
# ============================================================

def _parse_work_year(value: Any) -> int | None:
    """Parse a valid positive integer year."""

    if value is None or isinstance(value, bool):
        return None

    try:
        year_decimal = Decimal(str(value).strip())

        if not year_decimal.is_finite():
            return None

        if year_decimal != year_decimal.to_integral_value():
            return None

        year = int(year_decimal)

    except (InvalidOperation, ValueError, TypeError):
        return None

    if year <= 0:
        return None

    return year


# ============================================================
# Main Validation Function
# ============================================================

def validate_problem_03(author_data: dict[str, Any]) -> dict:
    """
    Detect unusually long work spans exceeding 80 years.

    Input:
        Extracted GET author response.

    Source:
        work_citation_history -> work_count_year
    """

    current_year = datetime.now().year

    # Get extracted yearly publication history
    work_history = author_data.get("work_citation_history")

    if not isinstance(work_history, dict):
        work_history = {}

    work_count_year = work_history.get("work_count_year")

    if not isinstance(work_count_year, dict):
        work_count_year = {}

    # Extract valid historical work years
    work_years = []

    for raw_year, raw_works_count in work_count_year.items():

        year = _parse_work_year(raw_year)

        # Exclude invalid and future years
        if year is None or year > current_year:
            continue

        # Consider only years with valid, positive publication counts
        if isinstance(raw_works_count, bool):
            continue

        try:
            count_decimal = Decimal(str(raw_works_count).strip())

            if (
                not count_decimal.is_finite()
                or count_decimal != count_decimal.to_integral_value()
                or count_decimal <= 0
            ):
                continue

        except (InvalidOperation, ValueError, TypeError):
            continue

        work_years.append(year)

    # Remove duplicate years
    work_years = sorted(set(work_years))

    # Check sufficient data
    if len(work_years) < 2:

        return {
            "problem_id": "P3",
            "problem_name": "Long Work Span (>80 Years)",
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": "Insufficient work-year data.",
            "evidence": {
                "total_years": len(work_years),
                "work_years": work_years,
                "minimum_year": None,
                "maximum_year": None,
                "work_span_years": None,
            },
        }

    # Calculate work span
    minimum_year = min(work_years)
    maximum_year = max(work_years)

    work_span = maximum_year - minimum_year

    # Determine validation flag
    flag = "Y" if work_span > 80 else "N"

    reason = (
        "Long Work Span Exceeds 80 Years"
        if flag == "Y"
        else "Work Span Does Not Exceed 80 Years"
    )

    # Return validation result
    return {
        "problem_id": "P3",
        "problem_name": "Long Work Span (>80 Years)",
        "flag": flag,
        "evaluation_status": "Evaluated",
        "reason": reason,
        "evidence": {
            "total_years": len(work_years),
            "work_years": work_years,
            "minimum_year": minimum_year,
            "maximum_year": maximum_year,
            "work_span_years": work_span,
            "threshold_years": 80,
        },
    }
