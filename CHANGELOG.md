# Changelog

All notable changes to csv-profiler are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-10-28

First stable release. A stdlib-only Python CLI that profiles CSV files:
column type inference, per-column statistics, duplicate detection,
data-quality warnings, Markdown reports and JSON output.

### Added
- CLI skeleton: read a CSV, report row/column counts
- Column type inference (integer, float, date, boolean, string)
- Per-column statistics (nulls, uniques, min/max/mean/median, top values)
- Duplicate row detection
- Data-quality warnings (high null %, constant columns, mixed types)
- Markdown report output (`--report report.md`)
- JSON output (`--json`)
- GitHub Actions CI (pytest on push, Python 3.10–3.12)
- Sample file `examples/people.csv` with example output in the README

### Fixed
- Clean CLI errors (exit 1, no tracebacks) for empty files, non-UTF-8
  files and duplicate headers; plain note for header-only files
- Loader rejects duplicate headers instead of silently merging columns
