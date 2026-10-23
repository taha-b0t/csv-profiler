"""Command-line interface for csv-profiler.

v0.1 first slice: read a CSV file and report its shape
(row count and column count). Profiling features land
incrementally per the roadmap in the README.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from . import __version__


def count_rows_and_columns(path: Path) -> tuple[int, int]:
    """Return (data_row_count, column_count) for a CSV file.

    The header row is not counted as a data row.
    """
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        if header is None:
            return 0, 0
        rows = sum(1 for _ in reader)
        return rows, len(header)


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

    rows, cols = count_rows_and_columns(path)
    print(f"file:    {path}")
    print(f"rows:    {rows}")
    print(f"columns: {cols}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
