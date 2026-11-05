
from typing import Any


# ============================================================
# Problem 5: ORCID Inconsistency
# ============================================================

def _normalize_orcid(value: Any) -> str | None:
    """Normalize an ORCID value for duplicate detection."""

    if not isinstance(value, str):
        return None

    value = value.strip()

    if not value:
        return None

    value = value.replace("https://orcid.org/", "")
    value = value.replace("http://orcid.org/", "")

    value = value.rstrip("/").strip()

    return value.upper() if value else None


# ============================================================
# Main Validation Function
# ============================================================

def validate_problem_05(author_data: dict[str, Any]) -> dict:
    """
    Detect multiple or excessive ORCID IDs.

    Problem 5.a: Multiple ORCID IDs (2–3 ORCIDs).
    Problem 5.b: Excessive ORCID IDs (>3 ORCIDs).

    Input:
        Extracted GET author response.

    Source:
        author_identity -> orcid, observed_orcids
    """

    # 1. Extract author identity

    author_identity = author_data.get("author_identity")

    if not isinstance(author_identity, dict):
        author_identity = {}

    primary_orcid = author_identity.get("orcid")
    observed_orcids = author_identity.get("observed_orcids")

    # 2. Collect and normalize ORCID IDs

    orcid_values = []

    if isinstance(primary_orcid, str):
        orcid_values.append(primary_orcid)

    if isinstance(observed_orcids, str):
        orcid_values.append(observed_orcids)

    elif isinstance(observed_orcids, list):
        orcid_values.extend(observed_orcids)

    unique_orcids = []
    seen_orcids = set()

    for value in orcid_values:

        normalized = _normalize_orcid(value)

        if normalized is None:
            continue

        if normalized not in seen_orcids:

            seen_orcids.add(normalized)
            unique_orcids.append(normalized)

    # 3. Count unique ORCID IDs

    orcid_count = len(unique_orcids)

    # 4. Determine validation result

    if 2 <= orcid_count <= 3:

        problem_id = "P5.a"
        problem_name = "Multiple ORCID IDs (2–3 ORCIDs)"
        flag = "Y"
        reason = "Multiple ORCID IDs"
        problem_category = "Problem 5.a"

    elif orcid_count > 3:

        problem_id = "P5.b"
        problem_name = "Excessive ORCID IDs (>3 ORCIDs)"
        flag = "Y"
        reason = "Excessive ORCID IDs"
        problem_category = "Problem 5.b"

    else:

        problem_id = "P5"
        problem_name = "ORCID Inconsistency"
        flag = "N"
        reason = "No ORCID Inconsistency"
        problem_category = None

    # 5. Return validation result

    return {
        "parent_problem_id": "P5",
        "parent_problem_name": "ORCID Inconsistency",
        "problem_id": problem_id,
        "problem_name": problem_name,
        "flag": flag,
        "evaluation_status": "Evaluated",
        "reason": reason,
        "details": f"Found {orcid_count} ORCID ID(s).",
        "evidence": {
            "total_orcid_count": orcid_count,
            "unique_orcids": unique_orcids,
            "problem_category": problem_category,
        },
    }
