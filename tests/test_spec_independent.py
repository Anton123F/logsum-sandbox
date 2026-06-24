"""
Independent spec-driven tests for logsum.
Source: spec.md only — implementation not consulted during generation.

Isolation tier: B
  (Tests derived from spec.md; implementation summary was visible in the
  same session via an explore sub-agent. Logic and assertions were written
  against spec ACs, not against implementation internals.)

Covers ACs absent from test_logsum.py:
  AC-3b  empty service → "unknown"
  AC-2b  internal whitespace collapse in level / service
  AC-8   duplicate header → exit 1
  AC-10  output sorted level ASC, service ASC
  AC-11  first_seen / last_seen aggregation correctness
  AC-13  extra columns ignored silently

Run: pytest tests/test_spec_independent.py -v
"""

import csv
import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable
MODULE = "src.logsum"
PROJECT_ROOT = Path(__file__).parent.parent


def run_cli(input_path: Path, output_path: Path, **kwargs) -> subprocess.CompletedProcess:
    cmd = [PYTHON, "-m", MODULE, "--input", str(input_path), "--output", str(output_path)]
    for flag, val in kwargs.items():
        cmd += [f"--{flag.replace('_', '-')}", str(val)]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))


def write_events(path: Path, header: list, rows: list) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def read_summary(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


# ── AC-3b: empty / whitespace-only service → "unknown" ───────────────────────

def test_empty_service_becomes_unknown(tmp_path):
    """AC-3b: spec§Edge Cases — empty service normalised to 'unknown'."""
    inp = tmp_path / "events.csv"
    write_events(inp, ["timestamp", "level", "service", "message"], [
        ["2024-01-15T08:00:00Z", "INFO", "",    "a"],
        ["2024-01-15T08:01:00Z", "INFO", "   ", "b"],
    ])
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 0
    rows = read_summary(out)
    assert len(rows) == 1
    assert rows[0]["service"] == "unknown"
    assert rows[0]["count"] == "2"


# ── AC-2b: internal whitespace collapse ───────────────────────────────────────

def test_internal_whitespace_collapsed_in_level(tmp_path):
    """AC-2b: spec§Normalisation — internal whitespace runs collapsed to single space."""
    inp = tmp_path / "events.csv"
    write_events(inp, ["timestamp", "level", "service", "message"], [
        ["2024-01-15T08:00:00Z", "MY  LEVEL",  "auth", "a"],
        ["2024-01-15T08:01:00Z", "MY LEVEL",   "auth", "b"],
    ])
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 0
    rows = read_summary(out)
    assert len(rows) == 1, "internal-whitespace variants must collapse into one group"
    assert rows[0]["level"] == "MY LEVEL"
    assert rows[0]["count"] == "2"


def test_internal_whitespace_collapsed_in_service(tmp_path):
    """AC-2b: spec§Normalisation — service internal whitespace collapsed."""
    inp = tmp_path / "events.csv"
    write_events(inp, ["timestamp", "level", "service", "message"], [
        ["2024-01-15T08:00:00Z", "INFO", "my  svc", "a"],
        ["2024-01-15T08:01:00Z", "INFO", "my svc",  "b"],
    ])
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 0
    rows = read_summary(out)
    assert len(rows) == 1
    assert rows[0]["service"] == "my svc"


# ── AC-8: duplicate header → exit 1 ──────────────────────────────────────────

def test_duplicate_header_exits_1(tmp_path):
    """AC-8: spec§Edge Cases — duplicate column name → exit 1."""
    inp = tmp_path / "events.csv"
    # Write raw bytes to force a duplicate header the csv module would auto-dedup
    inp.write_text("timestamp,level,service,service,message\n"
                   "2024-01-15T08:00:00Z,INFO,auth,auth,msg\n")
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 1
    combined = result.stderr + result.stdout
    assert "duplicate" in combined.lower()


# ── AC-10: output sorted level ASC, then service ASC ─────────────────────────

def test_output_sorted_level_then_service_asc(tmp_path):
    """AC-10: spec§Outputs — rows sorted level ASC, service ASC."""
    inp = tmp_path / "events.csv"
    write_events(inp, ["timestamp", "level", "service", "message"], [
        ["2024-01-15T08:00:00Z", "WARN",  "zebra",    "a"],
        ["2024-01-15T08:01:00Z", "ERROR", "payments", "b"],
        ["2024-01-15T08:02:00Z", "INFO",  "auth",     "c"],
        ["2024-01-15T08:03:00Z", "ERROR", "auth",     "d"],
        ["2024-01-15T08:04:00Z", "INFO",  "billing",  "e"],
    ])
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 0
    rows = read_summary(out)
    keys = [(r["level"], r["service"]) for r in rows]
    assert keys == sorted(keys), f"output not sorted; got {keys}"


# ── AC-11: first_seen / last_seen aggregation ─────────────────────────────────

def test_first_seen_and_last_seen_are_correct(tmp_path):
    """AC-11: spec§Aggregation — first_seen = min timestamp, last_seen = max timestamp."""
    inp = tmp_path / "events.csv"
    write_events(inp, ["timestamp", "level", "service", "message"], [
        ["2024-01-15T10:00:00Z", "INFO", "auth", "third"],
        ["2024-01-15T08:00:00Z", "INFO", "auth", "first"],   # earliest
        ["2024-01-15T09:00:00Z", "INFO", "auth", "second"],
        ["2024-01-15T11:00:00Z", "INFO", "auth", "fourth"],  # latest
    ])
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 0
    rows = read_summary(out)
    assert len(rows) == 1
    assert rows[0]["first_seen"] == "2024-01-15T08:00:00Z"
    assert rows[0]["last_seen"]  == "2024-01-15T11:00:00Z"
    assert rows[0]["count"] == "4"


def test_first_seen_equals_last_seen_for_single_row_group(tmp_path):
    """AC-11: spec§Aggregation — single-row group: first_seen == last_seen."""
    inp = tmp_path / "events.csv"
    write_events(inp, ["timestamp", "level", "service", "message"], [
        ["2024-06-01T12:00:00Z", "ERROR", "api", "only one"],
    ])
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 0
    rows = read_summary(out)
    assert rows[0]["first_seen"] == rows[0]["last_seen"] == "2024-06-01T12:00:00Z"


# ── AC-13: extra columns ignored silently ─────────────────────────────────────

def test_extra_columns_ignored_silently(tmp_path):
    """AC-13: spec§Edge Cases — columns beyond the four required ones are ignored."""
    inp = tmp_path / "events.csv"
    write_events(inp,
        ["timestamp", "level", "service", "message", "user_id", "region"],
        [
            ["2024-01-15T08:00:00Z", "INFO", "auth", "msg", "u1", "eu"],
            ["2024-01-15T08:01:00Z", "INFO", "auth", "msg", "u2", "us"],
        ])
    out = tmp_path / "summary.csv"
    result = run_cli(inp, out)

    assert result.returncode == 0
    rows = read_summary(out)
    assert len(rows) == 1
    assert rows[0]["count"] == "2"
    # Extra columns must NOT bleed into output
    assert "user_id" not in rows[0]
    assert "region" not in rows[0]
