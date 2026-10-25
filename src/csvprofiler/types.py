"""Infer a type for each column of a loaded CSV table.

Types, checked in order for the non-empty values of a column:

- ``integer`` — optional sign, digits only (``-42``, ``+7``)
- ``float`` — anything else that parses as a float (``3.14``, ``1e3``,
  ``.5``); integers are a subset of floats, so a column mixing
  ``1`` and ``2.5`` is a float, not a mixed-type column
- ``date`` — ISO dates/datetimes or common day-first / month-first
  formats (``2026-10-25``, ``25/10/2026``, ``10/25/2026``)
- ``boolean`` — ``true``/``false``, ``yes``/``no``, ``y``/``n``,
  ``t``/``f`` (case-insensitive); ``1``/``0`` are integers, not booleans
- ``string`` — anything else, including genuinely mixed values

Empty and whitespace-only values are treated as missing and ignored
by inference. A column with no non-empty values is ``unknown``.
"""

from __future__ import annotations

from datetime import datetime

from .loader import Table

BOOLEAN_WORDS = {
    "true",
    "false",
    "yes",
    "no",
    "y",
    "n",
    "t",
    "f",
}

DATE_FORMATS = (
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
    "%d %b %Y",
    "%d %B %Y",
)


def _is_missing(value: str) -> bool:
    return value.strip() == ""


def _is_integer(value: str) -> bool:
    text = value.strip()
    digits = text[1:] if text[:1] in ("+", "-") else text
    return digits.isdigit() and digits != ""


def _is_float(value: str) -> bool:
    text = value.strip()
    if text.lower() in ("nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"):
        return False
    try:
        float(text)
    except ValueError:
        return False
    return True


def _is_date(value: str) -> bool:
    text = value.strip()
    try:
        datetime.fromisoformat(text)
    except ValueError:
        pass
    else:
        return True
    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(text, fmt)
        except ValueError:
            continue
        return True
    return False


def _is_boolean(value: str) -> bool:
    return value.strip().lower() in BOOLEAN_WORDS


def infer_column_type(values: list[str]) -> str:
    """Infer the type of one column from its raw string values."""
    present = [v for v in values if not _is_missing(v)]
    if not present:
        return "unknown"
    if all(_is_integer(v) for v in present):
        return "integer"
    if all(_is_float(v) for v in present):
        return "float"
    if all(_is_date(v) for v in present):
        return "date"
    if all(_is_boolean(v) for v in present):
        return "boolean"
    return "string"


def infer_types(table: Table) -> dict[str, str]:
    """Return ``{column_name: inferred_type}`` for every column."""
    return {name: infer_column_type(table.data[name]) for name in table.columns}
