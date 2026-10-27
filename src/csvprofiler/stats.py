"""Per-column statistics for a loaded CSV table.

For every column this computes:

- ``count`` — number of non-missing values
- ``nulls`` and ``null_pct`` — missing values and their share of rows
- ``unique`` — number of distinct non-missing values
- numeric columns (integer/float): ``min_value``, ``max_value``,
  ``mean`` and ``median`` over the parsed numbers
- string columns: ``top_values`` — the five most common values with
  their counts, most frequent first

Empty and whitespace-only values count as missing, matching the
type inference in :mod:`csvprofiler.types`. A column with no rows
at all has count 0, null_pct 0.0 and no numeric or top-value stats.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from statistics import mean, median

from .loader import Table
from .types import infer_column_type

TOP_VALUE_LIMIT = 5


def _is_missing(value: str) -> bool:
    return value.strip() == ""


@dataclass
class ColumnStats:
    """Statistics for one column."""

    name: str
    count: int = 0
    nulls: int = 0
    null_pct: float = 0.0
    unique: int = 0
    min_value: float | None = None
    max_value: float | None = None
    mean: float | None = None
    median: float | None = None
    top_values: list[tuple[str, int]] = field(default_factory=list)


def column_stats(name: str, values: list[str]) -> ColumnStats:
    """Compute statistics for one column's raw string values."""
    total = len(values)
    present = [v for v in values if not _is_missing(v)]
    nulls = total - len(present)
    stats = ColumnStats(
        name=name,
        count=len(present),
        nulls=nulls,
        null_pct=(nulls / total * 100) if total else 0.0,
        unique=len(set(present)),
    )
    if not present:
        return stats

    column_type = infer_column_type(values)
    if column_type in ("integer", "float"):
        numbers = [float(v) for v in present]
        stats.min_value = min(numbers)
        stats.max_value = max(numbers)
        stats.mean = mean(numbers)
        stats.median = median(numbers)
    elif column_type == "string":
        stats.top_values = Counter(present).most_common(TOP_VALUE_LIMIT)
    return stats


def profile_stats(table: Table) -> dict[str, ColumnStats]:
    """Return ``{column_name: ColumnStats}`` for every column."""
    return {name: column_stats(name, table.data[name]) for name in table.columns}
