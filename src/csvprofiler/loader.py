"""Load a CSV file into column-oriented data.

The profiler works column by column, so the loader transposes the
row-oriented ``csv`` output up front: one list of raw string values
per column, in file order. Short rows are padded with empty strings
and overlong rows are truncated to the header width, so every column
always has exactly ``row_count`` values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import csv


@dataclass
class Table:
    """A CSV file in column-oriented form."""

    columns: list[str] = field(default_factory=list)
    data: dict[str, list[str]] = field(default_factory=dict)

    @property
    def row_count(self) -> int:
        """Number of data rows (the header row is not counted)."""
        if not self.columns:
            return 0
        return len(self.data[self.columns[0]])

    @property
    def column_count(self) -> int:
        return len(self.columns)


def read_csv(path: Path) -> Table:
    """Read ``path`` and return its columns and per-column values.

    An empty file yields an empty table; a header-only file yields
    columns with no values. A UTF-8 byte-order mark is stripped so
    the first column name is not polluted by it. A header with a
    repeated column name raises ValueError: the column-oriented
    table keys values by name, so a duplicate would silently
    merge two columns' values.
    """
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        if header is None:
            return Table()

        seen: set[str] = set()
        for name in header:
            if name in seen:
                raise ValueError(f"duplicate column name: '{name}'")
            seen.add(name)

        data: dict[str, list[str]] = {name: [] for name in header}
        width = len(header)
        for row in reader:
            if len(row) < width:
                row = row + [""] * (width - len(row))
            elif len(row) > width:
                row = row[:width]
            for name, value in zip(header, row):
                data[name].append(value)
        return Table(columns=header, data=data)
