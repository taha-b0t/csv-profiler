# csv-profiler

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

Current behavior: reads the file, reports the row and column counts,
and infers each column's type (integer, float, date, boolean, string).
Profiling features land incrementally — see the roadmap below.

## Roadmap

- [x] CLI skeleton: read a CSV, report row/column counts
- [x] Column type inference (integer, float, date, boolean, string)
- [ ] Per-column statistics (nulls, uniques, min/max/mean, top values)
- [ ] Duplicate row detection
- [ ] Data-quality warnings (high null %, constant columns, mixed types)
- [ ] Markdown report output (`--report report.md`)
- [ ] JSON output (`--json`)
- [ ] GitHub Actions CI
- [ ] v1.0.0 release

## Development

```bash
pip install -e .
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).
