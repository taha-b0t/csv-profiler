"""Tests for per-column statistics, including edge cases."""

import pytest

from csvprofiler.loader import Table
from csvprofiler.stats import column_stats, profile_stats


def test_integer_column_stats():
    stats = column_stats("age", ["18", "45", "29", ""])
    assert stats.count == 3
    assert stats.nulls == 1
    assert stats.null_pct == pytest.approx(25.0)
    assert stats.unique == 3
    assert stats.min_value == 18.0
    assert stats.max_value == 45.0
    assert stats.mean == pytest.approx(30.6666667)
    assert stats.median == 29.0
    assert stats.top_values == []


def test_float_column_stats():
    stats = column_stats("score", ["1.5", "2.5", "2.5"])
    assert stats.count == 3
    assert stats.nulls == 0
    assert stats.null_pct == 0.0
    assert stats.unique == 2
    assert stats.min_value == 1.5
    assert stats.max_value == 2.5
    assert stats.mean == pytest.approx(2.1666667)
    assert stats.median == 2.5


def test_median_of_even_count_averages_middle_two():
    stats = column_stats("n", ["1", "2", "3", "4"])
    assert stats.median == 2.5


def test_string_column_top_values():
    stats = column_stats(
        "city", ["Paris", "Lyon", "Paris", "Nice", "Paris", "Lyon"]
    )
    assert stats.count == 6
    assert stats.unique == 3
    assert stats.top_values == [("Paris", 3), ("Lyon", 2), ("Nice", 1)]
    assert stats.min_value is None
    assert stats.mean is None


def test_top_values_capped_at_five():
    values = [f"v{i}" for i in range(10)] + ["v0"]
    stats = column_stats("label", values)
    assert len(stats.top_values) == 5
    assert stats.top_values[0] == ("v0", 2)


def test_whitespace_only_counts_as_missing():
    stats = column_stats("x", ["1", "   ", "3"])
    assert stats.count == 2
    assert stats.nulls == 1
    assert stats.null_pct == pytest.approx(33.3333333)


def test_all_missing_column_has_no_numeric_stats():
    stats = column_stats("empty", ["", "   ", ""])
    assert stats.count == 0
    assert stats.nulls == 3
    assert stats.null_pct == 100.0
    assert stats.unique == 0
    assert stats.min_value is None
    assert stats.mean is None
    assert stats.top_values == []


def test_empty_column_has_zero_null_pct():
    stats = column_stats("empty", [])
    assert stats.count == 0
    assert stats.nulls == 0
    assert stats.null_pct == 0.0


def test_duplicate_values_lower_unique_count():
    stats = column_stats("n", ["5", "5", "5"])
    assert stats.count == 3
    assert stats.unique == 1


def test_profile_stats_covers_every_column():
    table = Table(
        columns=["age", "city"],
        data={"age": ["20", "30"], "city": ["Paris", "Lyon"]},
    )
    stats = profile_stats(table)
    assert set(stats) == {"age", "city"}
    assert stats["age"].mean == 25.0
    assert stats["city"].top_values == [("Paris", 1), ("Lyon", 1)]
