import re
import unicodedata
from typing import Any


# ============================================================
# Problem 8: Name Quality Mismatch
# ============================================================

PLACEHOLDER_TERMS = {
    "not available", "not known", "not specified", "not provided",
    "not disclosed", "no author", "no name", "no data",
    "unknown author", "anonymous author", "various authors",
}

SINGLE_PLACEHOLDER_WORDS = {
    "unknown", "anonymous", "anon", "unnamed", "unidentified",
    "undisclosed", "none", "null", "na", "no", "name", "author",
    "person", "user", "not", "available", "known", "missing",
    "placeholder", "dummy", "test", "deleted", "removed", "data",
    "various", "inconnu", "anonyme", "anonimo", "desconocido",
    "desconhecido", "unbekannt", "sconosciuto", "onbekend",
    "неизвестный", "неизвестно", "анонимный", "未知", "匿名", "不明",
}

STRONG_KEYWORDS = {
    "university", "universite", "universidad", "universidade",
    "universitat", "universita", "universiteit", "universitet",
    "universitas", "universiti", "universitetet", "университет",
    "πανεπιστήμιο", "大学", "대학교",
    "college", "collegio", "colegio", "faculdade", "hochschule",
    "колледж", "学院",
    "institute", "institut", "instituto", "instituut", "instytut",
    "институт", "研究所", "معهد",
    "library", "bibliotheque", "biblioteca", "bibliothek", "biblioteka",
    "библиотека", "图书馆", "図書館",
    "museum", "musee", "museo", "muzeum", "музей", "博物馆", "博物館",
    "hospital", "hopital", "ospedale", "krankenhaus", "больница", "医院",
    "academy", "academie", "academia", "akademie", "академия", "科学院",
    "laboratory", "laboratoire", "laboratorio", "laboratorium",
    "лаборатория", "实验室",
    "ministry", "ministere", "ministerio", "ministerium", "ministero",
    "министерство", "government agency", "research institute",
    "research center", "research centre", "centro de investigacion",
    "centre de recherche", "forschungszentrum", "research laboratory",
    "school", "escuela", "ecole", "scuola", "schule", "школа", "学校",
    "faculty", "faculte", "facultad",
}

INSTITUTION_GUARD_EXCEPTIONS = {
    "university", "universite", "universidad", "universidade",
    "universitat", "universita", "universiteit", "universitet",
    "universitas", "universiti", "университет", "大学", "대학교",
    "college", "collegio", "colegio", "faculdade", "hochschule",
    "колледж", "学院",
    "library", "bibliotheque", "biblioteca", "bibliothek", "biblioteka",
    "библиотека", "图书馆", "図書館",
    "museum", "musee", "museo", "muzeum", "музей", "博物馆", "博物館",
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(
        ch for ch in value
        if not unicodedata.combining(ch)
    )
    return " ".join(
        re.sub(r"[^\w]+", " ", value, flags=re.UNICODE).split()
    )


def _tokens(value: str) -> list[str]:
    return re.findall(r"[^\W_]+", value, flags=re.UNICODE)


_NORMALIZED_PLACEHOLDER_PHRASES = sorted(
    (
        tuple(_tokens(_normalize_text(term)))
        for term in PLACEHOLDER_TERMS
        if _tokens(_normalize_text(term))
    ),
    key=lambda phrase: -len(phrase),
)

_NORMALIZED_SINGLE_PLACEHOLDERS = {
    _normalize_text(term)
    for term in SINGLE_PLACEHOLDER_WORDS
}


def _is_placeholder_name(name: str) -> bool:
    """Match the entire name using placeholder words or phrases."""

    words = _tokens(_normalize_text(name))

    if not words:
        return False

    reachable = {0}

    for index in range(len(words)):

        if index not in reachable:
            continue

        if words[index] in _NORMALIZED_SINGLE_PLACEHOLDERS:
            reachable.add(index + 1)

        for phrase in _NORMALIZED_PLACEHOLDER_PHRASES:

            end = index + len(phrase)

            if tuple(words[index:end]) == phrase:
                reachable.add(end)

    return len(words) in reachable


def _keyword_matches(name: str, keywords: set[str]) -> list[str]:
    """Match complete words or phrases, not arbitrary substrings."""

    padded_name = f" {_normalize_text(name)} "

    return [
        keyword
        for keyword in sorted(keywords)
        if f" {_normalize_text(keyword)} " in padded_name
    ]


def _is_surname_initial_format(name: str) -> bool:
    """Recognize surname and initials formats."""

    cleaned = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", name)

    cleaned = re.sub(
        r",?\s*\b(?:ed|eds|editor|editors)\.?\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    if "," not in cleaned:
        return False

    surname, initials_part = cleaned.split(",", 1)
    initials = _tokens(_normalize_text(initials_part))

    return (
        bool(surname.strip())
        and 1 <= len(initials) <= 4
        and all(
            len(token) == 1 and token.isalpha()
            for token in initials
        )
    )

# ============================================================
# MAIN VALIDATION FUNCTION
# ============================================================

def validate_problem_08(author_data: dict[str, Any]) -> dict:
    """
    Detect Name Quality Mismatch.

    Subtype A: Placeholder Terms
    Subtype B: No Alphabetic Characters
    Subtype C: Single Character
    Subtype D: Institutional or Organisational Names

    Input:
        Extracted GET author response.

    Source:
        author_identity -> author_id, author_name
    """

    if not isinstance(author_data, dict):
        raise ValueError("author_data must be a dictionary.")

    # 1. Extract author identity

    author_identity = author_data.get("author_identity")

    if not isinstance(author_identity, dict):
        author_identity = {}

    author_id = author_identity.get("author_id")
    raw_name = author_identity.get("author_name")

    author_name = (
        raw_name if isinstance(raw_name, str) else None
    )

    name = author_name.strip() if author_name else ""

    # 2. Missing author name

    if not name:

        return {
            "problem_id": "P8",
            "problem_name": "Name Quality Mismatch",
            "author_id": author_id,
            "author_name": author_name,
            "flag": None,
            "evaluation_status": "Not Evaluated",
            "reason": (
                "Author name is missing; "
                "name-quality checks could not be performed."
            ),
            "evidence": {
                "detected_subtypes": [],
                "matched_keywords": [],
            },
        }

    # 3. Initialize detection

    detected_subtypes = []

    matched_keywords = _keyword_matches(
        name,
        STRONG_KEYWORDS,
    )

    exception_matches = _keyword_matches(
        name,
        INSTITUTION_GUARD_EXCEPTIONS,
    )

    # 4. Subtype A — Placeholder Terms

    if _is_placeholder_name(name):
        detected_subtypes.append("A")

    # 5. Subtype B — No Alphabetic Characters

    if not any(character.isalpha() for character in name):
        detected_subtypes.append("B")

    # 6. Subtype C — Single Character

    if sum(character.isalnum() for character in name) == 1:
        detected_subtypes.append("C")

    # 7. Subtype D — Institutional or Organisational Names

    person_name_guard = (
        bool(matched_keywords)
        and not exception_matches
        and _is_surname_initial_format(name)
    )

    if matched_keywords and not person_name_guard:
        detected_subtypes.append("D")

    # 8. Determine final flag and reason

    flag = "Y" if detected_subtypes else "N"

    reason = (
        "Name Quality Mismatch ("
        + ", ".join(
            f"Subtype {subtype}"
            for subtype in detected_subtypes
        )
        + ")"
        if detected_subtypes
        else "No name quality mismatch detected"
    )

    # 9. Return validation result

    return {
        "problem_id": "P8",
        "problem_name": "Name Quality Mismatch",
        "author_id": author_id,
        "author_name": author_name,
        "flag": flag,
        "evaluation_status": "Evaluated",
        "reason": reason,
        "evidence": {
            "detected_subtypes": detected_subtypes,
            "matched_keywords": matched_keywords,
            "institution_guard_exceptions": exception_matches,
            "person_name_guard_applied": person_name_guard,
        },
    }