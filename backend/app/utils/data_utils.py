import json
import math

from decimal import Decimal, InvalidOperation
from typing import Any


def normalize_text(value: Any) -> str | None:
    """
    Normalize text by removing leading/trailing whitespace.

    Returns None for missing, empty, or non-text container values.
    """
    if value is None:
        return None

    if isinstance(value, (dict, list, tuple, set)):
        return None

    if not isinstance(value, str):
        value = str(value)

    value = value.strip()

    return value if value else None


def as_list(value: Any) -> list:
    """
    Convert a value into a list.

    None       -> []
    [1, 2]     -> [1, 2]
    (1, 2)     -> [1, 2]
    "ABC"      -> ["ABC"]
    123        -> [123]
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, (tuple, set)):
        return list(value)

    return [value]


def parse_json_field(value: Any, default: Any = None) -> Any:
    """
    Parse a JSON string into a Python object.

    If the value is already a dictionary or list,
    return it unchanged.
    """

    if isinstance(value, (dict, list)):
        return value

    if not isinstance(value, str):
        return default

    value = value.strip()

    if not value:
        return default

    try:
        return json.loads(value)

    except (json.JSONDecodeError, TypeError):
        return default


def to_int(value: Any) -> int | None:
    """
    Safely convert an integer-like value into an integer.

    Accepts:
    - Integers
    - Integral floats
    - Numeric strings

    Rejects:
    - Booleans
    - None
    - Non-numeric values
    - Non-integral numbers
    """

    if value is None or isinstance(value, bool):
        return None

    try:
        number = Decimal(str(value).strip())

        if not number.is_finite():
            return None

        if number != number.to_integral_value():
            return None

        return int(number)

    except (InvalidOperation, ValueError, TypeError):
        return None


def normalize_year(value: Any) -> int | None:
    """
    Normalize a year value into an integer.

    Does not remove historical or future years.
    Year-range validation is handled separately.
    """

    return to_int(value)


def normalize_count(value: Any) -> int | None:
    """
    Normalize a count value into an integer.

    Does not impose a minimum or maximum count.
    """

    return to_int(value)


def normalize_country_code(value: Any) -> str | None:
    """
    Normalize a country code to uppercase.
    """

    value = normalize_text(value)

    if value is None:
        return None

    return value.upper()


def unique_preserve_order(values: Any) -> list:
    """
    Remove duplicate values while preserving their original order.

    Supports both hashable and unhashable values.
    """

    result = []
    seen = set()

    for value in as_list(values):

        try:
            if value in seen:
                continue

            seen.add(value)

        except TypeError:
            if value in result:
                continue

        result.append(value)

    return result


def get_nested(data: Any, *keys: str, default: Any = None) -> Any:
    """
    Safely retrieve a value from nested dictionaries.

    Example:
        get_nested(data, "ids", "orcid")
    """

    current = data

    for key in keys:

        if not isinstance(current, dict):
            return default

        current = current.get(key)

        if current is None:
            return default

    return current


def normalize_float(value: Any) -> float | None:
    """
    Safely convert a value into a finite float.
    """

    if value is None or isinstance(value, bool):
        return None

    try:
        result = float(value)

        if not math.isfinite(result):
            return None

        return result

    except (ValueError, TypeError, OverflowError):
        return None


def year_key(value: Any) -> str:
    """
    Preserve original year values as dictionary keys,
    including invalid and missing values.
    """

    if value is None:
        return "None"

    return str(value).strip()

