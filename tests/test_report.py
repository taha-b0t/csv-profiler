"""Tests for the Markdown report generator."""

from pathlib import Path

from csvprofiler.loader import read_csv
from csvprofiler.report import generate_report


def write_csv(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "sample.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_report_has_overview_columns_and_warnings(tmp_path):
    path = write_csv(tmp_path, "age,city\n30,Paris\n25,Paris\n,Paris\n")
    report = generate_report(read_csv(path))
    assert "# CSV profile" in report
    assert "## Overview" in report
    assert "- Rows: 3" in report
    assert "- Columns: 2" in report
    assert "## Columns" in report
    assert "## Warnings" in report


def test_report_column_table_carries_types_and_stats(tmp_path):
    path = write_csv(tmp_path, "age,city\n30,Paris\n25,Paris\n,Paris\n")
    report = generate_report(read_csv(path))
    assert "| age | integer | 2 | 1 | 33.3 | 2 | 25 | 30 | 27.5 | 27.5 |" in report
    assert "| city | string | 3 | 0 | 0.0 | 1 | " in report
    assert "Paris (3)" in report


def test_report_lists_warnings(tmp_path):
    path = write_csv(tmp_path, "age,flag\n30,yes\n30,yes\n")
    report = generate_report(read_csv(path))
    assert "duplicate row(s) found" in report
    assert "constant" in report


def test_report_clean_file_has_no_warnings_section_items(tmp_path):
    path = write_csv(tmp_path, "age,city\n30,Paris\n25,Lyon\n")
    report = generate_report(read_csv(path))
    assert "No warnings found." in report


def test_report_empty_file(tmp_path):
    path = write_csv(tmp_path, "")
    report = generate_report(read_csv(path))
    assert "- Rows: 0" in report
    assert "- Columns: 0" in report
    assert "No columns." in report
    assert "No warnings found." in report
