"""Tests for the column-oriented CSV loader."""

from csvprofiler.loader import Table, read_csv


def write_csv(tmp_path, text, name="sample.csv"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_reads_columns_and_values(tmp_path):
    path = write_csv(tmp_path, "name,age\nalice,30\nbob,25\n")
    table = read_csv(path)
    assert table.columns == ["name", "age"]
    assert table.data == {"name": ["alice", "bob"], "age": ["30", "25"]}
    assert table.row_count == 2
    assert table.column_count == 2


def test_empty_file(tmp_path):
    table = read_csv(write_csv(tmp_path, ""))
    assert table == Table()
    assert table.row_count == 0
    assert table.column_count == 0


def test_header_only(tmp_path):
    table = read_csv(write_csv(tmp_path, "a,b,c\n"))
    assert table.columns == ["a", "b", "c"]
    assert table.data == {"a": [], "b": [], "c": []}
    assert table.row_count == 0


def test_short_rows_are_padded(tmp_path):
    table = read_csv(write_csv(tmp_path, "a,b,c\n1,2\n3,4,5\n"))
    assert table.data["c"] == ["", "5"]


def test_long_rows_are_truncated(tmp_path):
    table = read_csv(write_csv(tmp_path, "a,b\n1,2,EXTRA\n"))
    assert table.data == {"a": ["1"], "b": ["2"]}


def test_bom_is_stripped_from_first_column(tmp_path):
    path = tmp_path / "bom.csv"
    path.write_bytes(b"\xef\xbb\xbfname,age\nalice,30\n")
    table = read_csv(path)
    assert table.columns == ["name", "age"]


def test_duplicate_header_raises(tmp_path):
    import pytest

    path = write_csv(tmp_path, "a,a\n1,2\n")
    with pytest.raises(ValueError, match="duplicate column name: 'a'"):
        read_csv(path)
