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
from .loader import read_csv
from .types import infer_types


def count_rows_and_columns(path: Path) -> tuple[int, int]:
    """Return (data_row_count, column_count) for a CSV file.

    The header row is not counted as a data row.
    """
    table = read_csv(path)
    return table.row_count, table.column_count


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
