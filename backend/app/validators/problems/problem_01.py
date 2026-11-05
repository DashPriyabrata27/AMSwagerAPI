
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any


# ============================================================
# Problem 1: Invalid or Future Work Years
# ============================================================

def _parse_work_year(value: Any) -> tuple[int | None, str | None]:

    if value is None:
        return None, "Missing year value"

    if isinstance(value, bool):
        return None, "Boolean value is not a valid year"

    try:
        year_decimal = Decimal(str(value).strip())

        if not year_decimal.is_finite():
            return None, "Non-finite year value"

        if year_decimal != year_decimal.to_integral_value():
            return None, "Non-integer year value"

        year = int(year_decimal)

    except (InvalidOperation, ValueError, TypeError):
        return None, "Unparseable year value"

    if year <= 0:
        return None, "Non-positive year value"

    return year, None


# ============================================================
# Main Validation Function
# ============================================================

def validate_problem_01(author_data: dict[str, Any]) -> dict:
    """
    Detect invalid or future affiliation years.

    Input:
        Extracted GET author response.

    Source:
        affiliations_details -> year
    """

    current_year = datetime.now().year

    # 1. Get extracted affiliation history
    affiliations_details = author_data.get("affiliations_details")

    if not isinstance(affiliations_details, list) or not affiliations_details:

        return {
            "problem_id": "P1",
            "problem_name": "Invalid or Future Work Years",
            "flag": "Not Evaluated",
            "details": "Affiliation-year history is missing or empty.",
            "evidence": {
                "current_year": current_year,
                "total_years_checked": 0,
                "invalid_years": [],
                "future_years": [],
            },
        }

    invalid_years = []
    future_years = []

    seen_valid_years = set()
    seen_invalid_years = set()

    # 2. Validate each affiliation year
    for affiliation in affiliations_details:

        if not isinstance(affiliation, dict):

            invalid_key = repr(affiliation)

            if invalid_key not in seen_invalid_years:
                seen_invalid_years.add(invalid_key)

                invalid_years.append({
                    "year": str(affiliation),
                    "reason": "Invalid affiliation record",
                })

            continue

        raw_year = affiliation.get("year")

        parsed_year, error_reason = _parse_work_year(raw_year)

        # Check invalid year
        if error_reason is not None:

            invalid_key = (
                type(raw_year).__name__,
                repr(raw_year),
            )

            if invalid_key not in seen_invalid_years:
                seen_invalid_years.add(invalid_key)

                invalid_years.append({
                    "year": str(raw_year),
                    "reason": error_reason,
                })

            continue

        # Check duplicate valid years
        if parsed_year in seen_valid_years:
            continue

        seen_valid_years.add(parsed_year)

        # Check future year
        if parsed_year > current_year:

            future_years.append({
                "year": parsed_year,
                "reason": "Affiliation year exceeds the current year",
            })

    # 3. Prepare evidence
    total_years_checked = (
        len(seen_valid_years) + len(invalid_years)
    )

    # 4. Determine validation result
    if invalid_years or future_years:

        flag = "Flagged"

        details = (
            f"Found {len(invalid_years)} invalid year(s) "
            f"and {len(future_years)} future year(s)."
        )

    else:

        flag = "Not Flagged"

        details = (
            f"No invalid or future affiliation years were found "
            f"among {total_years_checked} unique year entries."
        )

    # 5. Return validation result
    return {
        "problem_id": "P1",
        "problem_name": "Invalid or Future Work Years",
        "flag": flag,
        "details": details,
        "evidence": {
            "current_year": current_year,
            "total_years_checked": total_years_checked,
            "invalid_years": invalid_years,
            "future_years": future_years,
        },
    }
