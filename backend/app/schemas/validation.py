from typing import Any, Literal

from pydantic import BaseModel, Field

# 1. DETECTED PROBLEM

class ProblemItem(BaseModel):

    problem_id: str
    problem_name: str
    evidence: dict[str, Any] = Field(default_factory=dict)

# 2. FINAL VALIDATION RESPONSE

class ValidationResponse(BaseModel):

    author_id: str
    author_name: str | None = None

    detected_problems: list[ProblemItem] = Field(
        default_factory=list
    )

    total_problems: int = Field(ge=0)
    total_score: int = Field(ge=0)

    label: Literal[
        "GOOD",
        "CANT SAY",
        "SUSPICIOUS",
    ]

    not_evaluated_problems: list[ProblemItem] | None = None