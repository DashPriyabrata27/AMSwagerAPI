
from datetime import datetime
from typing import Any


# ============================================================
# Problem 10: 5 or More Countries in One Year
# ============================================================

COUNTRY_THRESHOLD = 5


# ============================================================
# Main Validation Function
# ============================================================

def validate_problem_10(author_data: dict[str, Any]) -> dict:
    """
    Detect authors affiliated with 5 or more countries
    in a single year.

    Input:
        Extracted GET author response.

    Source:
        country_details -> country_year

    Condition:
        Country count >= 5 in any single year.
    """

    # 1. Extract country-year information

    country_details = author_data.get("country_details")

    if not isinstance(country_details, dict):
        country_details = {}

    country_year = country_details.get("country_year")

    if not isinstance(country_year, dict) or not country_year:

        return {
            "problem_id": "P10",
            "problem_name": "5 or More Countries in One Year",
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": "Country-year information is missing or empty.",
            "evidence": {
                "country_threshold": COUNTRY_THRESHOLD,
                "yearly_country_counts": [],
                "suspicious_years": [],
            },
        }

    # 2. Collect unique countries for each year

    current_year = datetime.now().year

    yearly_countries = {}

    for raw_year, country_codes in country_year.items():

        # Validate year
        try:
            year = int(raw_year)

        except (ValueError, TypeError):
            continue

        # Exclude invalid, current and future years
        if year <= 0 or year >= current_year:
            continue

        if not isinstance(country_codes, list):
            continue

        # Collect unique country codes
        yearly_countries[year] = {
            code.strip().upper()
            for code in country_codes
            if isinstance(code, str) and code.strip()
        }

    # 3. Calculate yearly country counts

    yearly_country_counts = []

    for year in sorted(yearly_countries):

        country_count = len(yearly_countries[year])

        yearly_country_counts.append({
            "year": year,
            "country_count": country_count,
            "country_codes": sorted(yearly_countries[year]),
        })

    if not yearly_country_counts:

        return {
            "problem_id": "P10",
            "problem_name": "5 or More Countries in One Year",
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": "No valid historical country information available.",
            "evidence": {
                "country_threshold": COUNTRY_THRESHOLD,
                "yearly_country_counts": [],
                "suspicious_years": [],
            },
        }

    # 4. Identify suspicious years

    suspicious_years = [
        item
        for item in yearly_country_counts
        if item["country_count"] >= COUNTRY_THRESHOLD
    ]

    # 5. Determine final validation result

    if suspicious_years:

        flag = "Y"
        reason = "5 or More Countries in One Year"

    else:

        flag = "N"
        reason = "No Year With 5 or More Countries"

    # 6. Return validation result

    return {
        "problem_id": "P10",
        "problem_name": "5 or More Countries in One Year",
        "flag": flag,
        "evaluation_status": "Evaluated",
        "reason": reason,
        "details": (
            f"Found {len(suspicious_years)} suspicious year(s)."
        ),
        "evidence": {
            "country_threshold": COUNTRY_THRESHOLD,
            "yearly_country_counts": yearly_country_counts,
            "suspicious_years": suspicious_years,
        },
    }
