
from datetime import datetime
from decimal import Decimal, InvalidOperation
from statistics import median
from typing import Any


# ============================================================
# Problem 2: Extremely Yearly Publication Burst
# ============================================================

def _parse_non_negative_integer(value: Any) -> int | None:
    """Parse a non-negative integer value."""

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

def validate_problem_02(author_data: dict[str, Any]) -> dict:
    """
    Detect unusually high yearly publication activity.

    Algorithm selection:
        0-1 valid historical years : Not Evaluated
        2-4 valid historical years : Problem 2.b
        5+ valid historical years : Problem 2.a

    Input:
        Extracted GET author response.

    Source:
        work_citation_history -> work_count_year
    """

    current_year = datetime.now().year

    # 1. Get extracted yearly publication history

    work_history = author_data.get("work_citation_history")

    if not isinstance(work_history, dict):
        work_history = {}

    work_count_year = work_history.get("work_count_year")

    if not isinstance(work_count_year, dict):
        work_count_year = {}

    # 2. Prepare valid historical publication data

    valid_yearly_data = []

    invalid_years = []
    current_years = []
    future_years = []
    invalid_works_counts = []

    for raw_year, raw_works_count in work_count_year.items():

        # Validate year
        year = _parse_non_negative_integer(raw_year)

        if year is None or year == 0:

            invalid_years.append({
                "year": str(raw_year),
                "reason": "Invalid year value",
            })

            continue

        # Exclude current year
        if year == current_year:

            current_years.append(year)
            continue

        # Exclude future years
        if year > current_year:

            future_years.append(year)
            continue

        # Validate yearly publication count
        works_count = _parse_non_negative_integer(
            raw_works_count
        )

        if works_count is None:

            invalid_works_counts.append({
                "year": year,
                "works_count": raw_works_count,
                "reason": "Invalid works_count value",
            })

            continue

        valid_yearly_data.append({
            "year": year,
            "works_count": works_count,
        })

    # 3. Prepare common evidence

    valid_year_count = len(valid_yearly_data)

    evidence = {
        "current_year": current_year,
        "total_years_checked": valid_year_count,
        "valid_historical_years": [
            item["year"] for item in valid_yearly_data
        ],
        "invalid_years": invalid_years,
        "excluded_current_years": current_years,
        "excluded_future_years": future_years,
        "invalid_works_counts": invalid_works_counts,
    }

    # 4. Check sufficient historical data

    if valid_year_count <= 1:

        return {
            "problem_id": "P2",
            "problem_name": "Extremely Yearly Publication Burst",
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": (
                "Insufficient data for Publication Burst Detection."
            ),
            "details": (
                f"Only {valid_year_count} valid historical year(s) "
                "are available. At least 2 are required."
            ),
            "evidence": evidence,
        }

    # Extract valid yearly publication counts

    works_counts = [
        item["works_count"] for item in valid_yearly_data
    ]

    # ========================================================
    # Problem 2.a: Long-Series Publication Burst (>= 5 Years)
    # ========================================================

    if valid_year_count >= 5:

        baseline_median = median(works_counts)

        baseline = max(baseline_median, 1)

        burst_years = []

        for item in valid_yearly_data:

            ratio = item["works_count"] / baseline

            if ratio >= 10:

                burst_years.append({
                    "year": item["year"],
                    "works_count": item["works_count"],
                    "ratio": ratio,
                })

        n_burst_years = len(burst_years)

        flag = "Y" if n_burst_years > 0 else "N"

        reason = (
            "Long-Series Publication Burst"
            if flag == "Y"
            else "No burst"
        )

        evidence.update({
            "algorithm": "Problem 2.a",
            "baseline_median": baseline_median,
            "baseline": baseline,
            "n_burst_years": n_burst_years,
            "Burst_year_count_value": [
                item["works_count"] for item in burst_years
            ],
            "burst_years": burst_years,
        })

        return {
            "problem_id": "P2.a",
            "problem_name": (
                "Extremely Yearly Publication Burst (10× Baseline)"
            ),
            "flag": flag,
            "evaluation_status": "Evaluated",
            "reason": reason,
            "details": (
                f"Found {n_burst_years} burst year(s) "
                "using the 10x baseline threshold."
                if flag == "Y"
                else "No burst years were found."
            ),
            "evidence": evidence,
        }

    # ========================================================
    # Problem 2.b: Short-Series Publication Burst (2–4 Years)
    # ========================================================

    peak_item = max(
        valid_yearly_data,
        key=lambda item: item["works_count"],
    )

    peak = peak_item["works_count"]

    total_yearly_works = sum(works_counts)

    # Remove one occurrence of the peak

    remaining_counts = works_counts.copy()
    remaining_counts.remove(peak)

    remaining_median = median(remaining_counts)

    # Calculate Peak Ratio

    if remaining_median > 0:

        peak_ratio = peak / remaining_median

    else:

        peak_ratio = None

    # Calculate Peak Share

    if total_yearly_works > 0:

        peak_share = peak / total_yearly_works

    else:

        peak_share = None

    # Both conditions must be satisfied

    burst_detected = (
        peak_ratio is not None
        and peak_share is not None
        and peak_ratio >= 10
        and peak_share >= 0.9
    )

    flag = "Y" if burst_detected else "N"

    reason = (
        "Short-Series Publication Burst"
        if burst_detected
        else "No burst"
    )

    evidence.update({
        "algorithm": "Problem 2.b",
        "peak": peak,
        "peak_year": peak_item["year"],
        "total_yearly_works": total_yearly_works,
        "remaining_median": remaining_median,
        "peak_ratio": peak_ratio,
        "peak_share": peak_share,
    })

    return {
        "problem_id": "P2.b",
        "problem_name": (
            "Short-Series Publication Burst Detection (2–4 Years)"
        ),
        "flag": flag,
        "evaluation_status": "Evaluated",
        "reason": reason,
        "details": (
            "Both peak ratio and peak share thresholds were satisfied."
            if burst_detected
            else "Peak ratio and peak share conditions were not both satisfied."
        ),
        "evidence": evidence,
    }
