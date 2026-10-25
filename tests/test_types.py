"""Tests for per-column type inference, including edge cases."""

import pytest

from csvprofiler.types import infer_column_type


@pytest.mark.parametrize(
    "values",
    [
        ["1", "2", "42"],
        ["-7", "+3", "0"],
        ["007", "10"],
    ],
)
def test_integer(values):
    assert infer_column_type(values) == "integer"


@pytest.mark.parametrize(
    "values",
    [
        ["1.5", "2.0", "3"],
        ["1e3", "2.5"],
        [".5", "1.0"],
        ["-0.25", "4"],
    ],
)
def test_float(values):
    assert infer_column_type(values) == "float"


@pytest.mark.parametrize(
    "values",
    [
        ["2026-10-25", "2026-01-01"],
        ["25/10/2026", "01/01/2026"],
        ["10/25/2026", "01/31/2026"],
        ["2026-10-25T09:30:00", "2026-01-01T00:00:00"],
    ],
)
def test_date(values):
    assert infer_column_type(values) == "date"


@pytest.mark.parametrize(
    "values",
    [
        ["true", "false"],
        ["TRUE", "False"],
        ["yes", "no"],
        ["y", "n"],
        ["t", "f"],
    ],
)
def test_boolean(values):
    assert infer_column_type(values) == "boolean"


def test_ones_and_zeros_are_integers_not_booleans():
    assert infer_column_type(["1", "0", "1"]) == "integer"


def test_mixed_int_and_string_is_string():
    assert infer_column_type(["1", "two", "3"]) == "string"


def test_mixed_date_and_string_is_string():
    assert infer_column_type(["2026-10-25", "yesterday"]) == "string"


def test_missing_values_are_ignored():
    assert infer_column_type(["1", "", "3"]) == "integer"
    assert infer_column_type(["true", "   ", "false"]) == "boolean"


def test_all_missing_is_unknown():
    assert infer_column_type(["", "   "]) == "unknown"
    assert infer_column_type([]) == "unknown"


def test_plain_text_is_string():
    assert infer_column_type(["alice", "bob"]) == "string"


def test_nan_and_inf_are_not_floats():
    assert infer_column_type(["nan", "1.5"]) == "string"
    assert infer_column_type(["inf", "2.0"]) == "string"
