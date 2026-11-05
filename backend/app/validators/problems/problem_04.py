
from datetime import datetime
from decimal import Decimal, InvalidOperation
from statistics import median, quantiles
from typing import Any


# ============================================================
# Problem 4: Extreme Affiliations Detection
# ============================================================

def _parse_affiliation_year(value: Any) -> int | None:
    """Parse a valid positive integer affiliation year."""

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


def _parse_institution_count(value: Any) -> int | None:
    """Parse a valid non-negative institution count."""

    if value is None or isinstance(value, bool):
        return None

    try:
        count_decimal = Decimal(str(value).strip())

        if not count_decimal.is_finite():
            return None

        if count_decimal != count_decimal.to_integral_value():
            return None

        count = int(count_decimal)

    except (InvalidOperation, ValueError, TypeError):
        return None

    if count < 0:
        return None

    return count


# ============================================================
# Main Validation Function
# ============================================================

def validate_problem_04(author_data: dict[str, Any]) -> dict:
    """
    Detect extreme yearly institutional affiliations.

    Input:
        Extracted GET author response.

    Source:
        affiliations_details -> year, institution_count

    Algorithm:
        MAD method when MAD > 0.
        IQR method when MAD = 0.
    """

    current_year = datetime.now().year

    # 1. Extract yearly affiliation details

    affiliations_details = author_data.get("affiliations_details")

    if not isinstance(affiliations_details, list):
        affiliations_details = []

    yearly_affiliation_data = []

    invalid_years = []
    current_years = []
    future_years = []
    invalid_institution_counts = []

    # 2. Prepare valid historical affiliation data

    for record in affiliations_details:

        if not isinstance(record, dict):
            continue

        raw_year = record.get("year")

        year = _parse_affiliation_year(raw_year)

        # Check invalid year
        if year is None:

            invalid_years.append(str(raw_year))
            continue

        # Exclude current year
        if year == current_year:

            current_years.append(year)
            continue

        # Exclude future year
        if year > current_year:

            future_years.append(year)
            continue

        # Read already calculated institution count
        institution_count = _parse_institution_count(
            record.get("institution_count")
        )

        if institution_count is None:

            invalid_institution_counts.append({
                "year": year,
                "institution_count": record.get("institution_count"),
            })

            continue

        yearly_affiliation_data.append({
            "year": year,
            "institution_count": institution_count,
        })

    # 3. Calculate yearly institution counts

    yearly_affiliation_data.sort(
        key=lambda item: item["year"]
    )

    affiliation_counts = [
        item["institution_count"]
        for item in yearly_affiliation_data
    ]

    valid_year_count = len(affiliation_counts)

    # 4. Prepare common evidence

    evidence = {
        "current_year": current_year,
        "total_years_checked": valid_year_count,
        "yearly_affiliation_counts": yearly_affiliation_data,
        "invalid_years": invalid_years,
        "excluded_current_years": current_years,
        "excluded_future_years": future_years,
        "invalid_institution_counts": invalid_institution_counts,
    }

    # 5. Check sufficient historical data

    if valid_year_count < 2:

        return {
            "problem_id": "P4",
            "problem_name": "Extreme Affiliations Detection",
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": "Insufficient historical affiliation data.",
            "details": (
                f"Only {valid_year_count} valid historical year(s) "
                "are available. At least 2 are required."
            ),
            "evidence": {
                **evidence,
                "yearly_median": None,
                "MAD": None,
                "robust_z_score": None,
                "Q1": None,
                "Q3": None,
                "IQR": None,
                "upper_fence": None,
                "threshold_method": "Not Evaluated",
                "suspicious_years": [],
            },
        }

    # 6. Calculate statistical measures

    yearly_median = median(affiliation_counts)

    MAD = median(
        abs(count - yearly_median)
        for count in affiliation_counts
    )

    quartile_values = quantiles(
        affiliation_counts,
        n=4,
        method="inclusive",
    )

    Q1 = quartile_values[0]
    Q3 = quartile_values[2]

    IQR = Q3 - Q1

    upper_fence = Q3 + (1.5 * IQR)

    suspicious_years = []
    robust_z_scores = None

    # 7. MAD Method (MAD > 0)

    if MAD > 0:

        threshold_method = "MAD"

        robust_z_scores = []

        for item in yearly_affiliation_data:

            count = item["institution_count"]

            robust_z_score = (
                0.6745 * (count - yearly_median)
            ) / MAD

            robust_z_scores.append({
                "year": item["year"],
                "institution_count": count,
                "robust_z_score": robust_z_score,
            })

            if robust_z_score >= 3.5:

                suspicious_years.append({
                    "year": item["year"],
                    "institution_count": count,
                    "robust_z_score": robust_z_score,
                })

    # 8. IQR Method (MAD = 0)

    else:

        threshold_method = "IQR"

        for item in yearly_affiliation_data:

            count = item["institution_count"]

            if count > upper_fence:

                suspicious_years.append({
                    "year": item["year"],
                    "institution_count": count,
                })

    # 9. Determine final validation result

    flag = "Y" if suspicious_years else "N"

    if flag == "Y":

        reason = "Extreme Affiliations Detected"

        details = (
            f"Extreme affiliations detected in "
            f"{len(suspicious_years)} year(s)."
        )

    else:

        reason = "No Extreme Affiliations Detected"

        details = "No extreme yearly affiliations were detected."

    # 10. Prepare final evidence

    evidence.update({
        "yearly_median": yearly_median,
        "MAD": MAD,
        "robust_z_score": robust_z_scores,
        "Q1": Q1,
        "Q3": Q3,
        "IQR": IQR,
        "upper_fence": upper_fence,
        "threshold_method": threshold_method,
        "suspicious_years": suspicious_years,
    })

    return {
        "problem_id": "P4",
        "problem_name": "Extreme Affiliations Detection",
        "flag": flag,
        "evaluation_status": "Evaluated",
        "reason": reason,
        "details": details,
        "evidence": evidence,
    }
