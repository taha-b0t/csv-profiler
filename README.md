# csv-profiler

[![Tests](https://github.com/taha-b0t/csv-profiler/actions/workflows/tests.yml/badge.svg)](https://github.com/taha-b0t/csv-profiler/actions/workflows/tests.yml)

A tiny data-quality profiler for CSV files. Pure Python, standard library only — no pandas, no dependencies.

Point it at a CSV and it tells you what you're actually working with: column types, missing values, duplicates, basic statistics, and the kind of quiet data problems that break pipelines later.

## Why

Every data project starts with "let me look at the file first." This tool makes that first look systematic instead of eyeballing rows in a spreadsheet.

## Install

```bash
pip install -e .
```

Requires Python 3.10+.

## Usage

```bash
csvprofiler data.csv
```

Save the same profile as a Markdown report:

```bash
csvprofiler data.csv --report report.md
```

Current behavior: reads the file, reports the row and column counts,
infers each column's type (integer, float, date, boolean, string),
and prints per-column statistics (nulls, uniques, min/max/mean/median
for numbers, top values for strings), then flags data-quality
warnings: duplicate rows, columns with over 30% missing values,
constant columns, and columns mixing value types.
Profiling features land incrementally — see the roadmap below.

## Example

A sample file ships in [`examples/people.csv`](examples/people.csv):

```csv
name,age,city,joined
Amina,28,Casablanca,2023-01-15
Youssef,34,Rabat,2022-06-01
Sara,,Marrakech,2024-03-10
Youssef,34,Rabat,2022-06-01
Omar,41,Tangier,2021-11-20
```

```bash
csvprofiler examples/people.csv
```

```text
file:    examples/people.csv
rows:    5
columns: 4
types:
  name: string
  age: integer
  city: string
  joined: date
stats:
  name:
    count: 5, nulls: 0 (0.0%), unique: 4
    top values: Youssef (2), Amina (1), Sara (1), Omar (1)
  age:
    count: 4, nulls: 1 (20.0%), unique: 3
    min: 28, max: 41, mean: 34.25, median: 34.0
  city:
    count: 5, nulls: 0 (0.0%), unique: 4
    top values: Rabat (2), Casablanca (1), Marrakech (1), Tangier (1)
  joined:
    count: 5, nulls: 0 (0.0%), unique: 4
warnings:
  - 1 duplicate row(s) found
```

One missing age, one duplicated row — spotted at a glance.

## Roadmap

- [x] CLI skeleton: read a CSV, report row/column counts
- [x] Column type inference (integer, float, date, boolean, string)
- [x] Per-column statistics (nulls, uniques, min/max/mean, top values)
- [x] Duplicate row detection
- [x] Data-quality warnings (high null %, constant columns, mixed types)
- [x] Markdown report output (`--report report.md`)
- [x] JSON output (`--json`)
- [x] GitHub Actions CI
- [x] v1.0.0 release

## Development

```bash
pip install -e .
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).
