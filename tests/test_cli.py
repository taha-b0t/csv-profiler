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
