"""Tests for duplicate-row detection and data-quality warnings."""

from csvprofiler.checks import count_duplicate_rows, profile_warnings
from csvprofiler.loader import Table


def table(columns, data):
    return Table(columns=columns, data=data)


def codes(warnings):
    return [w.code for w in warnings]


def test_no_duplicates_in_distinct_rows():
    t = table(["a", "b"], {"a": ["1", "2"], "b": ["x", "y"]})
    assert count_duplicate_rows(t) == 0


def test_duplicate_rows_count_beyond_first_occurrence():
    t = table(
        ["a", "b"],
        {"a": ["1", "1", "1", "2"], "b": ["x", "x", "x", "y"]},
    )
    assert count_duplicate_rows(t) == 2


def test_rows_differing_in_one_column_are_not_duplicates():
    t = table(["a", "b"], {"a": ["1", "1"], "b": ["x", "y"]})
    assert count_duplicate_rows(t) == 0


def test_empty_and_header_only_tables_have_no_duplicates():
    assert count_duplicate_rows(table([], {})) == 0
    assert count_duplicate_rows(table(["a"], {"a": []})) == 0


def test_clean_table_has_no_warnings():
    t = table(
        ["age", "city"],
        {"age": ["20", "30", "40"], "city": ["Paris", "Lyon", "Nice"]},
    )
    assert profile_warnings(t) == []


def test_high_nulls_warning_above_30_percent():
    t = table(["x", "y"], {"x": ["1", "", "", ""], "y": ["a", "b", "c", "d"]})
    warnings = profile_warnings(t)
    assert "high_nulls" in codes(warnings)
    high = [w for w in warnings if w.code == "high_nulls"][0]
    assert high.column == "x"
    assert "75.0%" in high.message


def test_nulls_at_exactly_30_percent_not_flagged():
    values = ["1"] * 7 + ["", "", ""]
    t = table(["x"], {"x": values})
    assert "high_nulls" not in codes(profile_warnings(t))


def test_constant_column_warning():
    t = table(["flag", "n"], {"flag": ["yes", "yes", "yes"], "n": ["1", "2", "3"]})
    warnings = profile_warnings(t)
    assert "constant_column" in codes(warnings)
    assert [w for w in warnings if w.code == "constant_column"][0].column == "flag"


def test_all_missing_column_is_not_constant():
    t = table(["x"], {"x": ["", "", ""]})
    assert "constant_column" not in codes(profile_warnings(t))


def test_mixed_types_warning_for_numbers_and_text():
    t = table(["v"], {"v": ["1", "abc", "2"]})
    warnings = profile_warnings(t)
    assert "mixed_types" in codes(warnings)


def test_uniform_string_column_is_not_mixed():
    t = table(["v"], {"v": ["apple", "banana", "cherry"]})
    assert "mixed_types" not in codes(profile_warnings(t))


def test_numeric_column_is_not_mixed():
    t = table(["v"], {"v": ["1", "2.5", "3"]})
    assert "mixed_types" not in codes(profile_warnings(t))


def test_duplicate_rows_warning_and_empty_table_has_none():
    t = table(["a"], {"a": ["1", "1", "2"]})
    warnings = profile_warnings(t)
    assert "duplicate_rows" in codes(warnings)
    assert "1 duplicate row(s)" in [w.message for w in warnings if w.code == "duplicate_rows"][0]
    assert profile_warnings(table(["a"], {"a": []})) == []
    assert profile_warnings(table([], {})) == []
