"""Smoke tests for the v0.1 CLI slice."""

from pathlib import Path

from csvprofiler.cli import count_rows_and_columns, main


def write_csv(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "sample.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_count_rows_and_columns(tmp_path):
    path = write_csv(tmp_path, "name,age\nalice,30\nbob,25\n")
    assert count_rows_and_columns(path) == (2, 2)


def test_count_empty_file(tmp_path):
    path = write_csv(tmp_path, "")
    assert count_rows_and_columns(path) == (0, 0)


def test_count_header_only(tmp_path):
    path = write_csv(tmp_path, "a,b,c\n")
    assert count_rows_and_columns(path) == (0, 3)


def test_main_prints_shape(tmp_path, capsys):
    path = write_csv(tmp_path, "x,y\n1,2\n3,4\n5,6\n")
    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "rows:    3" in out
    assert "columns: 2" in out


def test_main_missing_file(capsys):
    assert main(["does-not-exist.csv"]) == 1
    assert "no such file" in capsys.readouterr().err


def test_main_empty_file_errors(tmp_path, capsys):
    path = write_csv(tmp_path, "")
    assert main([str(path)]) == 1
    assert "empty" in capsys.readouterr().err


def test_main_undecodable_file_errors_without_traceback(tmp_path, capsys):
    path = tmp_path / "bad.csv"
    path.write_bytes(b"\xff\xfe not utf-8\n")
    assert main([str(path)]) == 1
    err = capsys.readouterr().err
    assert "not valid UTF-8" in err
    assert "Traceback" not in err


def test_main_duplicate_header_errors(tmp_path, capsys):
    path = write_csv(tmp_path, "a,a\n1,2\n")
    assert main([str(path)]) == 1
    assert "duplicate column name: 'a'" in capsys.readouterr().err


def test_main_prints_inferred_types(tmp_path, capsys):
    path = write_csv(
        tmp_path, "name,age,joined,active\nada,36,2026-01-15,true\n"
    )
    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "types:" in out
    assert "  name: string" in out
    assert "  age: integer" in out
    assert "  joined: date" in out
    assert "  active: boolean" in out


def test_main_prints_no_warnings_for_clean_file(tmp_path, capsys):
    path = write_csv(tmp_path, "age,city\n30,Paris\n25,Lyon\n")
    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "warnings:" in out
    assert "  none" in out


def test_main_prints_warnings_for_dirty_file(tmp_path, capsys):
    path = write_csv(
        tmp_path,
        "age,flag,mix\n30,yes,1\n30,yes,1\n30,yes,abc\n,yes,3\n",
    )
    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "warnings:" in out
    assert "duplicate row(s)" in out
    assert "constant" in out
    assert "mixes value types" in out


def test_main_report_flag_writes_markdown_file(tmp_path, capsys):
    path = write_csv(tmp_path, "age,city\n30,Paris\n25,Lyon\n")
    report_path = tmp_path / "report.md"
    assert main([str(path), "--report", str(report_path)]) == 0
    out = capsys.readouterr().out
    assert f"report:  {report_path}" in out
    report = report_path.read_text(encoding="utf-8")
    assert "# CSV profile" in report
    assert "## Overview" in report
    assert "## Columns" in report
    assert "## Warnings" in report
    assert "| age | integer |" in report


def test_main_json_flag_prints_parseable_profile(tmp_path, capsys):
    import json

    path = write_csv(tmp_path, "age,city\n30,Paris\n25,Lyon\n")
    assert main([str(path), "--json"]) == 0
    profile = json.loads(capsys.readouterr().out)
    assert profile["row_count"] == 2
    assert profile["column_count"] == 2
    by_name = {column["name"]: column for column in profile["columns"]}
    assert by_name["age"]["type"] == "integer"
    assert by_name["age"]["mean"] == 27.5
    assert by_name["city"]["top_values"] == [["Paris", 1], ["Lyon", 1]]


def test_main_json_flag_with_report_keeps_stdout_pure_json(tmp_path, capsys):
    import json

    path = write_csv(tmp_path, "age\n30\n25\n")
    report_path = tmp_path / "report.md"
    assert main([str(path), "--json", "--report", str(report_path)]) == 0
    profile = json.loads(capsys.readouterr().out)
    assert profile["row_count"] == 2
    assert "# CSV profile" in report_path.read_text(encoding="utf-8")


def test_main_prints_per_column_stats(tmp_path, capsys):
    path = write_csv(
        tmp_path, "age,city\n30,Paris\n25,Paris\n,Paris\n"
    )
    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "stats:" in out
    assert "count: 2, nulls: 1 (33.3%), unique: 2" in out
    assert "min: 25, max: 30, mean: 27.5, median: 27.5" in out
    assert "top values: Paris (3)" in out
