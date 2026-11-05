from typing import Any

from app.validators.rule_engine import run_all_validations
from app.scoring.scoring_engine import calculate_score
from app.scoring.weights import PROBLEM_NAMES



# 1. VALIDATE INPUT DATA
def _validate_input(
    author_data: dict[str, Any],
) -> dict[str, str | None]:

    if not isinstance(author_data, dict):
        raise ValueError("Author data must be a dictionary.")

    identity = author_data.get("author_identity")

    if not isinstance(identity, dict):
        raise ValueError("Author identity details are missing.")

    author_id = identity.get("author_id")
    author_name = identity.get("author_name")

    if not isinstance(author_id, str) or not author_id.strip():
        raise ValueError("Author ID is missing.")

    if not isinstance(author_name, str):
        author_name = None

    return {
        "author_id": author_id.strip(),
        "author_name": author_name.strip() if author_name else None,
    }



# 2. RUN VALIDATION ENGINE
def _run_validation_engine(
    author_data: dict[str, Any],
) -> list[dict]:

    output = run_all_validations(author_data=author_data)

    if not isinstance(output, dict):
        raise TypeError("Rule engine must return a dictionary.")

    results = output.get("results")

    if not isinstance(results, list):
        raise TypeError("Rule engine results must be a list.")

    if not all(isinstance(item, dict) for item in results):
        raise TypeError("Invalid validation result.")

    return results



# 3. RUN SCORING ENGINE
def _run_scoring_engine(
    validation_results: list[dict],
) -> dict:

    result = calculate_score(validation_results)

    if not isinstance(result, dict):
        raise TypeError("Scoring engine must return a dictionary.")

    return result


# 4. PREPARE FINAL RESPONSE

def _prepare_response(
    author_identity: dict,
    validation_results: list[dict],
    scoring_result: dict,
) -> dict:

    # 1. Collect detected problems
    detected_problems = []

    for result in validation_results:

        status = str(
            result.get("evaluation_status") or ""
        ).strip().casefold()

        flag = str(
            result.get("flag") or ""
        ).strip().casefold()

        if status == "evaluated" and flag in {"y", "yes", "flagged"}:

            problem_id = str(
                result.get("problem_id") or ""
            ).strip()

            if not problem_id:
                raise ValueError("Detected problem is missing problem_id.")

            detected_problems.append({
                "problem_id": problem_id,
                "problem_name": (
                    result.get("problem_name")
                    or result.get("name")
                    or PROBLEM_NAMES.get(problem_id, problem_id)
                ),
                "evidence": result.get("evidence") or {},
            })

    # 2. Get classification from scoring engine
    raw_label = (
        scoring_result.get("classification")
        or scoring_result.get("label")
    )

    if not isinstance(raw_label, str):
        raise ValueError(
            f"Scoring classification is missing: {scoring_result}"
        )

    classification = (
        raw_label.strip()
        .casefold()
        .replace("'", "")
        .replace("_", " ")
    )

    labels = {
        "good": "GOOD",
        "cant say": "CANT SAY",
        "suspicious": "SUSPICIOUS",
    }

    if classification not in labels:
        raise ValueError(
            f"Invalid scoring classification: {raw_label}"
        )

    # 3. Validate total score
    total_score = scoring_result.get("total_score")

    if (
        isinstance(total_score, bool)
        or not isinstance(total_score, int)
        or total_score < 0
    ):
        raise ValueError("Invalid total score.")

    # 4. Prepare final response
    response = {
        "author_id": author_identity["author_id"],
        "author_name": author_identity["author_name"],
        "detected_problems": detected_problems,
        "total_problems": len(detected_problems),
        "total_score": total_score,
        "label": labels[classification],
    }

    # 5. Include unevaluated problems only when present
    not_evaluated = scoring_result.get(
        "not_evaluated_problems", []
    )

    if not_evaluated:
        response["not_evaluated_problems"] = [
            {
                "problem_id": item.get("problem_id"),
                "problem_name": (
                    item.get("name")
                    or item.get("problem_name")
                    or PROBLEM_NAMES.get(
                        item.get("problem_id"), item.get("problem_id")
                    )
                ),
            }
            for item in not_evaluated
        ]

    return response

# ============================================================
# 5. MAIN VALIDATION SERVICE
# ============================================================

def run_author_validation(
    author_data: dict[str, Any],
) -> dict:

    author_identity = _validate_input(author_data)

    validation_results = _run_validation_engine(author_data)

    scoring_result = _run_scoring_engine(validation_results)

    return _prepare_response(
        author_identity,
        validation_results,
        scoring_result,
    )