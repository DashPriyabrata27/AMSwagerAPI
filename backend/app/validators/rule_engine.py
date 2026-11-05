
from typing import Any, Callable


# ============================================================
# 1. IMPORT VALIDATION FUNCTIONS
# ============================================================

from app.validators.problems.problem_01 import validate_problem_01
from app.validators.problems.problem_02 import validate_problem_02
from app.validators.problems.problem_03 import validate_problem_03
from app.validators.problems.problem_04 import validate_problem_04
from app.validators.problems.problem_05 import validate_problem_05
from app.validators.problems.problem_06 import validate_problem_06
from app.validators.problems.problem_07 import validate_problem_07
from app.validators.problems.problem_08 import validate_problem_08
from app.validators.problems.problem_09 import validate_problem_09
from app.validators.problems.problem_10 import validate_problem_10


# ============================================================
# 2. PROBLEM REGISTRY
# ============================================================

PROBLEM_REGISTRY: list[tuple[str, Callable]] = [

    ("P1", validate_problem_01),
    ("P2", validate_problem_02),
    ("P3", validate_problem_03),
    ("P4", validate_problem_04),
    ("P5", validate_problem_05),
    ("P6", validate_problem_06),
    ("P7", validate_problem_07),
    ("P8", validate_problem_08),
    ("P9", validate_problem_09),
    ("P10", validate_problem_10),

]


# ============================================================
# 3. AUTHOR INFORMATION
# ============================================================

def _get_author_identity(
    author_data: dict[str, Any],
) -> tuple[str | None, str | None]:
    """Extract author identity from the GET response."""

    author_identity = author_data.get("author_identity")

    if not isinstance(author_identity, dict):
        raise ValueError("Author identity details are missing.")

    author_id = author_identity.get("author_id")
    author_name = author_identity.get("author_name")

    return author_id, author_name


# ============================================================
# 4. NORMALIZE VALIDATION RESULT
# ============================================================

def _normalize_result(
    result: dict,
    expected_problem_id: str,
) -> dict:
    """
    Standardize validator outputs.

    Standard flags:
        Y       -> Flagged
        N       -> Not Flagged
        None    -> Not Evaluated

    Preserve individual problem IDs such as:
        P2.a, P2.b, P5.a and P5.b.
    """

    result = dict(result)

    result.setdefault("problem_id", expected_problem_id)

    raw_flag = result.get("flag")

    if isinstance(raw_flag, str):

        normalized_flag = raw_flag.strip().casefold()

        if normalized_flag in {"y", "yes", "flagged"}:
            result["flag"] = "Y"

        elif normalized_flag in {"n", "no", "not flagged"}:
            result["flag"] = "N"

        elif normalized_flag == "not evaluated":
            result["flag"] = None

    # Normalize evaluation status

    status = result.get("evaluation_status")

    if status is None:

        result["evaluation_status"] = (
            "Not Evaluated"
            if result.get("flag") is None
            else "Evaluated"
        )

    else:

        status_text = str(status).strip()

        if status_text.casefold().startswith("not evaluated"):

            result["evaluation_status"] = "Not Evaluated"
            result["flag"] = None

        elif status_text.casefold() == "evaluated":

            result["evaluation_status"] = "Evaluated"

    return result


# ============================================================
# 5. EXECUTE INDIVIDUAL PROBLEM
# ============================================================

def _execute_problem(
    problem_id: str,
    validator: Callable,
    author_data: dict[str, Any],
) -> dict:
    """Execute one validation problem independently."""

    try:

        result = validator(author_data)

        if not isinstance(result, dict):
            raise TypeError(
                f"{problem_id} did not return a dictionary."
            )

        return _normalize_result(result, problem_id)

    except Exception as exc:

        return {
            "problem_id": problem_id,
            "problem_name": problem_id,
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": (
                "Validation could not be completed "
                "because an internal error occurred."
            ),
            "error": str(exc),
        }


# ============================================================
# 6. EXECUTE ALL REGISTERED PROBLEMS
# ============================================================

def run_all_validations(
    author_data: dict[str, Any],
) -> dict:
    """
    Execute all registered validation problems.

    Input:
        Extracted nine-field GET author response.

    Output:
        Consolidated validation results and summary.
    """

    # 1. Validate input

    if not isinstance(author_data, dict):

        raise ValueError(
            "Author data must be a dictionary."
        )

    # 2. Extract author identity

    author_id, author_name = _get_author_identity(
        author_data
    )

    # 3. Execute all registered problems

    results = []

    for problem_id, validator in PROBLEM_REGISTRY:

        result = _execute_problem(
            problem_id=problem_id,
            validator=validator,
            author_data=author_data,
        )

        results.append(result)

    # 4. Calculate evaluation summary

    evaluated_count = 0
    not_evaluated_count = 0

    flagged_count = 0
    not_flagged_count = 0

    for result in results:

        evaluation_status = result.get(
            "evaluation_status",
            "Not Evaluated",
        )

        flag = result.get("flag")

        if evaluation_status == "Evaluated":

            evaluated_count += 1

        else:

            not_evaluated_count += 1

        if flag == "Y":

            flagged_count += 1

        elif flag == "N":

            not_flagged_count += 1

    # 5. Return consolidated results

    return {

        "author_id": author_id,
        "author_name": author_name,

        "validation_summary": {
            "total_problems": len(results),
            "evaluated_count": evaluated_count,
            "not_evaluated_count": not_evaluated_count,
            "flagged_count": flagged_count,
            "not_flagged_count": not_flagged_count,
        },

        "results": results,

    }
