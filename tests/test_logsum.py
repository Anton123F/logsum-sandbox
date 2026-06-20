"""
Tests for logsum CLI — derived purely from spec.md.
Run: pytest tests/test_logsum.py -v
"""

import csv
import subprocess
import sys
from pathlib import Path

import pytest

PYTHON = sys.executable
MODULE = "src.logsum"
PROJECT_ROOT = Path(__file__).parent.parent
FIXTURES = Path(__file__).parent / "fixtures"


# ── helpers ───────────────────────────────────────────────────────────────────

def run_cli(input_path: Path, output_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, "-m", MODULE, "--input", str(input_path), "--output", str(output_path)],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )


def write_events(path: Path, header: list, rows: list) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def read_summary(path: Path) -> list:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


# ── 1. Grouping: same (level, service) collapses into one row ─────────────────

def test_basic_grouping(tmp_path):
    out = tmp_path / "summary.csv"
    result = run_cli(FIXTURES / "basic_events.csv", out)

    assert result.returncode == 0
    rows = read_summary(out)
    by_key = {(r["level"], r["service"]): r for r in rows}
    assert by_key[("INFO", "auth")]["count"] == "2"
    assert by_key[("ERROR", "payments")]["count"] == "1"


# ── 2. Normalisation: level→upper, service→lower, whitespace stripped/collapsed

def test_normalisation_merges_case_and_whitespace_variants(tmp_path):
    inp = tmp_path / "events.csv"
    write_events(inp, ["timestamp", "level", "service", "message"], [
        ["2024-01-15T08:00:00Z", "  warn  ", "  Auth  ", "a"],
        ["2024-01-15T08:01:00Z", "WARN",     "auth",     "b"],
    ])
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 0
    rows = read_summary(out)
    assert len(rows) == 1, "case/whitespace variants must collapse into one group"
    assert rows[0]["level"] == "WARN"
    assert rows[0]["service"] == "auth"
    assert rows[0]["count"] == "2"


# ── 3. Missing level: empty or whitespace-only → "UNKNOWN" ───────────────────

def test_empty_level_becomes_UNKNOWN(tmp_path):
    inp = tmp_path / "events.csv"
    write_events(inp, ["timestamp", "level", "service", "message"], [
        ["2024-01-15T08:00:00Z", "",    "auth", "a"],
        ["2024-01-15T08:01:00Z", "   ", "auth", "b"],
    ])
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 0
    rows = read_summary(out)
    assert len(rows) == 1
    assert rows[0]["level"] == "UNKNOWN"
    assert rows[0]["count"] == "2"


# ── 4. Malformed timestamp: row skipped + warning to stderr ──────────────────

def test_malformed_timestamp_row_skipped_with_stderr_warning(tmp_path):
    inp = tmp_path / "events.csv"
    write_events(inp, ["timestamp", "level", "service", "message"], [
        ["2024-01-15T08:00:00Z", "INFO", "auth", "good"],
        ["not-a-timestamp",      "INFO", "auth", "bad"],   # row 3 in file
        ["2024-01-15T09:00:00Z", "INFO", "auth", "good"],
    ])
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 0
    rows = read_summary(out)
    assert rows[0]["count"] == "2", "malformed-timestamp row must not be counted"
    assert "WARN" in result.stderr, "warning must be emitted to stderr"
    assert "skipped" in result.stderr.lower()


# ── 5. Empty input (header only): header-only summary.csv, exit 0 ────────────

def test_header_only_input_writes_empty_summary(tmp_path):
    inp = tmp_path / "events.csv"
    write_events(inp, ["timestamp", "level", "service", "message"], [])
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 0
    assert out.exists(), "summary.csv must be created even for empty input"
    rows = read_summary(out)
    assert rows == []


# ── 6. Missing required column → exit 1 with column name in message ──────────

def test_missing_required_column_exits_1(tmp_path):
    inp = tmp_path / "events.csv"
    write_events(inp, ["timestamp", "level", "message"], [   # 'service' absent
        ["2024-01-15T08:00:00Z", "INFO", "msg"],
    ])
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 1
    combined = result.stderr + result.stdout
    assert "service" in combined.lower()


# ── 7. Input file not found → exit 1 ─────────────────────────────────────────

def test_input_file_not_found_exits_1(tmp_path):
    missing = tmp_path / "ghost.csv"
    out = tmp_path / "summary.csv"
    result = run_cli(missing, out)

    assert result.returncode == 1
    combined = result.stderr + result.stdout
    assert "not found" in combined.lower()


# ── 8. CLI --output flag writes summary to the specified path ─────────────────

def test_cli_output_flag_writes_to_custom_path(tmp_path):
    custom_out = tmp_path / "subdir" / "out.csv"
    custom_out.parent.mkdir(parents=True)
    result = run_cli(FIXTURES / "basic_events.csv", custom_out)

    assert result.returncode == 0
    assert custom_out.exists(), "--output path must receive the summary file"
    rows = read_summary(custom_out)
    assert len(rows) > 0
