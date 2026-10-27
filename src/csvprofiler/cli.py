"""Command-line interface for csv-profiler.

v0.1 first slice: read a CSV file and report its shape
(row count and column count). Profiling features land
incrementally per the roadmap in the README.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .checks import profile_warnings
from .loader import read_csv
from .stats import profile_stats
from .types import infer_types


def count_rows_and_columns(path: Path) -> tuple[int, int]:
    """Return (data_row_count, column_count) for a CSV file.

    The header row is not counted as a data row.
    """
    table = read_csv(path)
    return table.row_count, table.column_count


def _format_number(value: float, column_type: str) -> str:
    """Render a numeric stat: integers without a decimal point."""
    if column_type == "integer":
        return str(int(value))
    return str(value)


def _print_stats(table, types) -> None:
    stats = profile_stats(table)
    print("stats:")
    for name in table.columns:
        s = stats[name]
        print(f"  {name}:")
        print(
            f"    count: {s.count}, nulls: {s.nulls} "
            f"({s.null_pct:.1f}%), unique: {s.unique}"
        )
        if s.min_value is not None:
            print(
                f"    min: {_format_number(s.min_value, types[name])}, "
                f"max: {_format_number(s.max_value, types[name])}, "
                f"mean: {s.mean}, median: {s.median}"
            )
        if s.top_values:
            top = ", ".join(f"{value} ({n})" for value, n in s.top_values)
            print(f"    top values: {top}")


def _print_warnings(table) -> None:
    warnings = profile_warnings(table)
    print("warnings:")
    if not warnings:
        print("  none")
        return
    for warning in warnings:
        print(f"  - {warning.message}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="csvprofiler",
        description="Profile a CSV file: shape, types, stats and data-quality checks.",
    )
    parser.add_argument("file", help="path to the CSV file to profile")
    parser.add_argument(
        "--version", action="version", version=f"csvprofiler {__version__}"
    )
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"error: no such file: {path}", file=sys.stderr)
        return 1

    table = read_csv(path)
    types = infer_types(table)
    print(f"file:    {path}")
    print(f"rows:    {table.row_count}")
    print(f"columns: {table.column_count}")
    if table.columns:
        print("types:")
        for name in table.columns:
            print(f"  {name}: {types[name]}")
        _print_stats(table, types)
        _print_warnings(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
