"""Markdown report generation for a profiled CSV table.

The report mirrors what the CLI prints to stdout — overview,
per-column types and statistics, and data-quality warnings —
in a form that can be saved, shared, or pasted into a document.
"""

from __future__ import annotations

from .checks import profile_warnings
from .loader import Table
from .stats import profile_stats
from .types import infer_types


def _format_number(value: float, column_type: str) -> str:
    """Render a numeric stat: integers without a decimal point."""
    if column_type == "integer":
        return str(int(value))
    return str(value)


def _format_stat(value: float | None, column_type: str) -> str:
    """Render a numeric stat, or an empty cell when absent.

    Min/max are whole numbers for integer columns; mean and
    median keep their fractional part, so callers pass them
    through :func:`str` instead of this helper.
    """
    if value is None:
        return ""
    return _format_number(value, column_type)


def _format_average(value: float | None) -> str:
    """Render a mean/median, or an empty cell when absent."""
    if value is None:
        return ""
    return str(value)


def generate_report(table: Table) -> str:
    """Return the Markdown profile report for ``table``.

    Sections, in order: overview (row/column counts), a per-column
    statistics table, and data-quality warnings. An empty table
    still yields a valid report with zero counts and no warnings.
    """
    types = infer_types(table)
    stats = profile_stats(table)
    warnings = profile_warnings(table)

    lines = ["# CSV profile", ""]
    lines.append("## Overview")
    lines.append("")
    lines.append(f"- Rows: {table.row_count}")
    lines.append(f"- Columns: {table.column_count}")
    lines.append("")

    lines.append("## Columns")
    lines.append("")
    if not table.columns:
        lines.append("No columns.")
        lines.append("")
    else:
        lines.append(
            "| Column | Type | Count | Nulls | Null % | Unique | "
            "Min | Max | Mean | Median | Top values |"
        )
        lines.append(
            "| --- | --- | --- | --- | --- | --- | "
            "--- | --- | --- | --- | --- |"
        )
        for name in table.columns:
            s = stats[name]
            top = ", ".join(f"{value} ({n})" for value, n in s.top_values)
            lines.append(
                f"| {name} | {types[name]} | {s.count} | {s.nulls} | "
                f"{s.null_pct:.1f} | {s.unique} | "
                f"{_format_stat(s.min_value, types[name])} | "
                f"{_format_stat(s.max_value, types[name])} | "
                f"{_format_average(s.mean)} | "
                f"{_format_average(s.median)} | {top} |"
            )
        lines.append("")

    lines.append("## Warnings")
    lines.append("")
    if not warnings:
        lines.append("No warnings found.")
    else:
        for warning in warnings:
            lines.append(f"- {warning.message}")
    lines.append("")
    return "\n".join(lines)
