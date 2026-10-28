"""Tests for the JSON profile builder."""

import json

import pytest

from csvprofiler.json_output import profile_to_dict
from csvprofiler.loader import read_csv


def write_csv(tmp_path, text):
    path = tmp_path / "sample.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_profile_to_dict_shape_and_types(tmp_path):
    path = write_csv(tmp_path, "name,age\nada,36\ngrace,40\n")
    profile = profile_to_dict(read_csv(path))
    assert profile["row_count"] == 2
    assert profile["column_count"] == 2
    by_name = {column["name"]: column for column in profile["columns"]}
    assert by_name["name"]["type"] == "string"
    assert by_name["age"]["type"] == "integer"
    assert by_name["age"]["min"] == 36
    assert by_name["age"]["max"] == 40
    assert by_name["age"]["mean"] == 38.0
    assert profile["warnings"] == []


def test_profile_to_dict_numeric_stats_and_nulls(tmp_path):
    path = write_csv(tmp_path, "age\n30\n25\n\n")
    profile = profile_to_dict(read_csv(path))
    column = profile["columns"][0]
    assert column["count"] == 2
    assert column["nulls"] == 1
    assert column["null_pct"] == pytest.approx(100 / 3)
    assert column["unique"] == 2
    assert column["top_values"] == []


def test_profile_to_dict_string_top_values(tmp_path):
    path = write_csv(tmp_path, "city\nParis\nLyon\nParis\n")
    column = profile_to_dict(read_csv(path))["columns"][0]
    assert column["top_values"] == [["Paris", 2], ["Lyon", 1]]
    assert column["min"] is None
    assert column["mean"] is None


def test_profile_to_dict_warnings(tmp_path):
    path = write_csv(tmp_path, "age\n30\n30\n")
    profile = profile_to_dict(read_csv(path))
    codes = [warning["code"] for warning in profile["warnings"]]
    assert "constant_column" in codes
    assert "duplicate_rows" in codes
    duplicate = next(w for w in profile["warnings"] if w["code"] == "duplicate_rows")
    assert duplicate["column"] is None
    assert "duplicate row(s)" in duplicate["message"]


def test_profile_to_dict_is_json_serialisable(tmp_path):
    path = write_csv(tmp_path, "age,city\n30,Paris\n25,Lyon\n")
    profile = profile_to_dict(read_csv(path))
    assert json.loads(json.dumps(profile)) == profile


def test_profile_to_dict_empty_file(tmp_path):
    path = write_csv(tmp_path, "")
    profile = profile_to_dict(read_csv(path))
    assert profile == {
        "row_count": 0,
        "column_count": 0,
        "columns": [],
        "warnings": [],
    }
