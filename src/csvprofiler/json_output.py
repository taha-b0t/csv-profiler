"""Machine-readable profile output for a loaded CSV table.

:func:`profile_to_dict` collects the same profile the CLI prints —
shape, per-column types and statistics, and data-quality warnings —
into a plain ``dict`` that serialises to JSON with no extra work,
so the profile can feed scripts and other tools.
"""

from __future__ import annotations

from .checks import profile_warnings
from .loader import Table
from .stats import profile_stats
from .types import infer_types


def profile_to_dict(table: Table) -> dict:
    """Return the profile of ``table`` as a JSON-friendly dict.

    Numeric stats are ``None`` when they do not apply (a string
    column has no min/max/mean/median; a column with no present
    values has no top values either). Warning entries carry their
    code and message, plus the column they concern, or ``None``
    for table-wide warnings such as duplicate rows.
    """
    types = infer_types(table)
    stats = profile_stats(table)
    warnings = profile_warnings(table)

    columns = []
    for name in table.columns:
        s = stats[name]
        columns.append(
            {
                "name": name,
                "type": types[name],
                "count": s.count,
                "nulls": s.nulls,
                "null_pct": s.null_pct,
                "unique": s.unique,
                "min": s.min_value,
                "max": s.max_value,
                "mean": s.mean,
                "median": s.median,
                "top_values": [[value, n] for value, n in s.top_values],
            }
        )

    return {
        "row_count": table.row_count,
        "column_count": table.column_count,
        "columns": columns,
        "warnings": [
            {
                "code": warning.code,
                "column": warning.column,
                "message": warning.message,
            }
            for warning in warnings
        ],
    }
