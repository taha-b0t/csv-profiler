"""Duplicate-row detection and data-quality warnings.

For a loaded CSV table this module answers two questions:

- how many rows are exact duplicates of an earlier row, and
- which columns look suspicious: a high share of missing values,
  a column that never changes, a column mixing value kinds, and
  any duplicate rows at all.

Thresholds are deliberately simple and documented so a user can
read a warning and know exactly what triggered it:

- ``HIGH_NULL_THRESHOLD_PCT`` — a column is flagged when more
  than 30% of its values are missing
- a column is constant when it has at least one present value and
  exactly one distinct value
- a column has mixed types when its inferred type is ``string``
  but its present values fall into two or more value kinds
  (integer, float, date, boolean, other text) — a column of
  ``1`` and ``2.5`` is a float, not a mixed column, because type
  inference already resolves it
- duplicate rows are counted as rows beyond the first occurrence
  of each distinct row, so three identical rows count as two
  duplicates
"""

from __future__ import annotations

from dataclasses import dataclass

from .loader import Table
from .stats import profile_stats
from .types import (
    _is_boolean,
    _is_date,
    _is_float,
    _is_integer,
    infer_column_type,
)

HIGH_NULL_THRESHOLD_PCT = 30.0


@dataclass
class Warning:
    """One data-quality warning."""

    code: str
    message: str
    column: str | None = None


def _rows(table: Table) -> list[tuple[str, ...]]:
    """Return the table's rows as tuples, in file order."""
    if not table.columns:
        return []
    return list(zip(*(table.data[name] for name in table.columns)))


def count_duplicate_rows(table: Table) -> int:
    """Return how many rows duplicate an earlier row.

    Three identical rows count as two duplicates; a table with no
    rows or no columns has zero duplicates.
    """
    rows = _rows(table)
    return len(rows) - len(set(rows))


def _value_kind(value: str) -> str:
    """Classify one present value, following inference order."""
    if _is_integer(value):
        return "integer"
    if _is_float(value):
        return "float"
    if _is_date(value):
        return "date"
    if _is_boolean(value):
        return "boolean"
    return "string"


def _is_mixed(values: list[str]) -> bool:
    """Return True when present values span two or more kinds."""
    present = [v for v in values if v.strip() != ""]
    if len(present) < 2:
        return False
    return len({_value_kind(v) for v in present}) > 1


def profile_warnings(table: Table) -> list[Warning]:
    """Return data-quality warnings for the table, in column order.

    Per-column warnings come first (high nulls, constant column,
    mixed types), followed by the duplicate-rows warning, if any.
    An empty or header-only table yields no warnings.
    """
    if not table.columns or table.row_count == 0:
        return []

    stats = profile_stats(table)
    warnings: list[Warning] = []
    for name in table.columns:
        values = table.data[name]
        s = stats[name]
        if s.null_pct > HIGH_NULL_THRESHOLD_PCT:
            warnings.append(
                Warning(
                    code="high_nulls",
                    column=name,
                    message=(
                        f"column '{name}' has {s.null_pct:.1f}% missing "
                        f"values ({s.nulls} of {table.row_count})"
                    ),
                )
            )
        if s.count > 0 and s.unique == 1:
            warnings.append(
                Warning(
                    code="constant_column",
                    column=name,
                    message=f"column '{name}' is constant: every value is the same",
                )
            )
        if infer_column_type(values) == "string" and _is_mixed(values):
            warnings.append(
                Warning(
                    code="mixed_types",
                    column=name,
                    message=f"column '{name}' mixes value types (e.g. numbers and text)",
                )
            )

    duplicates = count_duplicate_rows(table)
    if duplicates > 0:
        warnings.append(
            Warning(
                code="duplicate_rows",
                message=f"{duplicates} duplicate row(s) found",
            )
        )
    return warnings
