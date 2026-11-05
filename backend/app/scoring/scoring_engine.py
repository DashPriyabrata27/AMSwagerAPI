from app.scoring.weights import (
    PROBLEM_NAMES,
    PROBLEM_WEIGHTS,
    SCORE_CLASSIFICATIONS,
)


def calculate_score(validation_results: list[dict]) -> dict:
    detected_problems = []
    not_evaluated_problems = []

    total_score = 0
    evaluation_complete = True
    seen_problems = set()

    expected_problems = {f"P{i}" for i in range(1, 11)}
    completed_problems = set()

    for result in validation_results:

        problem_id = str(result.get("problem_id", "")).strip()

        if not problem_id:
            raise ValueError("Missing problem_id.")

        if problem_id in seen_problems:
            raise ValueError(f"Duplicate problem: {problem_id}")

        seen_problems.add(problem_id)

        parent_id = problem_id.split(".")[0]
        completed_problems.add(parent_id)

        problem_name = (
            result.get("problem_name")
            or result.get("name")
            or PROBLEM_NAMES.get(problem_id, problem_id)
        )

        status = str(
            result.get("evaluation_status", "")
        ).strip().casefold()

        flag = str(result.get("flag") or "").strip().upper()

        # Handle validations that could not be performed.
        if status != "evaluated" or flag not in {"Y", "N"}:

            evaluation_complete = False

            not_evaluated_problems.append({
                "problem_id": problem_id,
                "problem_name": problem_name
            })

            continue

        # Only flagged problems are included.
        if flag == "Y":

            detected_problems.append({
                "problem_id": problem_id,
                "problem_name": problem_name
            })

            weight = PROBLEM_WEIGHTS.get(problem_id)

            if weight is None:
                evaluation_complete = False
                continue

            if isinstance(weight, bool) or not isinstance(weight, int) or weight < 0:
                raise ValueError(f"Invalid weight for {problem_id}")

            total_score += weight

    # Detect missing validation results.
    missing_problems = expected_problems - completed_problems

    for problem_id in sorted(missing_problems):
        evaluation_complete = False

        not_evaluated_problems.append({
            "problem_id": problem_id,
            "problem_name": PROBLEM_NAMES.get(
                problem_id, "Validation result missing"
            )
        })

    # Read classification thresholds from weights.py.
    good = SCORE_CLASSIFICATIONS["GOOD"]
    cant_say = SCORE_CLASSIFICATIONS["CANT_SAY"]
    suspicious = SCORE_CLASSIFICATIONS["SUSPICIOUS"]

    if total_score >= suspicious["min_score"] and (
        suspicious["max_score"] is None
        or total_score <= suspicious["max_score"]
    ):
        label = "SUSPICIOUS"

    elif not evaluation_complete:
        label = "CANT SAY"

    elif cant_say["min_score"] <= total_score <= cant_say["max_score"]:
        label = "CANT SAY"

    elif good["min_score"] <= total_score <= good["max_score"]:
        label = "GOOD"

    else:
        raise ValueError(f"Score does not match any classification: {total_score}")

    output = {
        "detected_problems": detected_problems,
        "total_problems": len(detected_problems),
        "total_score": total_score,
        "label": label
    }

    # Include this only when validations are incomplete.
    if not_evaluated_problems:
        output["not_evaluated_problems"] = not_evaluated_problems

    return output