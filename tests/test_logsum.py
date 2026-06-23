import csv
import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable
MODULE = "src.logsum"
PROJECT_ROOT = Path(__file__).parent.parent
FIXTURES = Path(__file__).parent / "fixtures"


def run_cli(input_path, output_path, min_count=None):
    cmd = [PYTHON, "-m", MODULE, "--input", str(input_path), "--output", str(output_path)]
    if min_count is not None:
        cmd += ["--min-count", str(min_count)]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))


def write_events(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def read_summary(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


HEADER = ["timestamp", "level", "service", "message"]


def test_basic_grouping(tmp_path):
    out = tmp_path / "out.csv"
    result = run_cli(FIXTURES / "basic_events.csv", out)
    assert result.returncode == 0
    rows = {(r["level"], r["service"]): r for r in read_summary(out)}
    assert rows[("INFO", "auth")]["count"] == "2"
    assert rows[("ERROR", "payments")]["count"] == "1"


def test_normalisation_collapses_variants(tmp_path):
    inp = tmp_path / "e.csv"
    write_events(inp, HEADER, [
        ["2024-01-15T08:00:00Z", "  warn  ", "  Auth  ", "a"],
        ["2024-01-15T08:01:00Z", "WARN",     "auth",     "b"],
    ])
    out = tmp_path / "out.csv"
    result = run_cli(inp, out)
    assert result.returncode == 0
    rows = read_summary(out)
    assert len(rows) == 1
    assert rows[0]["level"] == "WARN" and rows[0]["service"] == "auth"


def test_empty_level_becomes_UNKNOWN(tmp_path):
    inp = tmp_path / "e.csv"
    write_events(inp, HEADER, [
        ["2024-01-15T08:00:00Z", "",    "auth", "a"],
        ["2024-01-15T08:01:00Z", "   ", "auth", "b"],
    ])
    out = tmp_path / "out.csv"
    assert run_cli(inp, out).returncode == 0
    rows = read_summary(out)
    assert len(rows) == 1 and rows[0]["level"] == "UNKNOWN" and rows[0]["count"] == "2"


def test_empty_service_becomes_unknown(tmp_path):
    inp = tmp_path / "e.csv"
    write_events(inp, HEADER, [["2024-01-15T08:00:00Z", "INFO", "   ", "a"]])
    out = tmp_path / "out.csv"
    assert run_cli(inp, out).returncode == 0
    assert read_summary(out)[0]["service"] == "unknown"


def test_bad_timestamp_skipped_with_warning(tmp_path):
    inp = tmp_path / "e.csv"
    write_events(inp, HEADER, [
        ["2024-01-15T08:00:00Z", "INFO", "auth", "good"],
        ["not-a-date",           "INFO", "auth", "bad"],
        ["2024-01-15T09:00:00Z", "INFO", "auth", "good"],
    ])
    out = tmp_path / "out.csv"
    result = run_cli(inp, out)
    assert result.returncode == 0
    assert read_summary(out)[0]["count"] == "2"
    assert "WARN" in result.stderr and "skipped" in result.stderr.lower()


def test_header_only_writes_empty_summary(tmp_path):
    inp = tmp_path / "e.csv"
    write_events(inp, HEADER, [])
    out = tmp_path / "out.csv"
    assert run_cli(inp, out).returncode == 0
    assert read_summary(out) == []


def test_missing_required_column_exits_1(tmp_path):
    inp = tmp_path / "e.csv"
    write_events(inp, ["timestamp", "level", "message"], [["2024-01-15T08:00:00Z", "INFO", "msg"]])
    out = tmp_path / "out.csv"
    result = run_cli(inp, out)
    assert result.returncode == 1
    assert "service" in (result.stderr + result.stdout).lower()


def test_duplicate_column_exits_1(tmp_path):
    inp = tmp_path / "e.csv"
    inp.write_text("timestamp,level,level,service,message\n2024-01-15T08:00:00Z,INFO,INFO,auth,msg\n")
    out = tmp_path / "out.csv"
    result = run_cli(inp, out)
    assert result.returncode == 1
    assert "duplicate" in (result.stderr + result.stdout).lower()


def test_input_not_found_exits_1(tmp_path):
    result = run_cli(tmp_path / "ghost.csv", tmp_path / "out.csv")
    assert result.returncode == 1
    assert "not found" in (result.stderr + result.stdout).lower()


def test_min_count_filters_below_threshold(tmp_path):
    inp = tmp_path / "e.csv"
    write_events(inp, HEADER, [
        ["2024-01-15T08:00:00Z", "ERROR", "auth", "a"],
        ["2024-01-15T08:01:00Z", "ERROR", "auth", "b"],
        ["2024-01-15T08:02:00Z", "INFO",  "api",  "c"],
    ])
    out = tmp_path / "out.csv"
    assert run_cli(inp, out, min_count=2).returncode == 0
    keys = [(r["level"], r["service"]) for r in read_summary(out)]
    assert ("ERROR", "auth") in keys and ("INFO", "api") not in keys


def test_min_count_exact_boundary(tmp_path):
    inp = tmp_path / "e.csv"
    write_events(inp, HEADER, [
        ["2024-01-15T08:00:00Z", "WARN", "db",  "a"],
        ["2024-01-15T08:01:00Z", "WARN", "db",  "b"],
        ["2024-01-15T08:02:00Z", "WARN", "db",  "c"],
        ["2024-01-15T08:03:00Z", "INFO", "api", "d"],
        ["2024-01-15T08:04:00Z", "INFO", "api", "e"],
    ])
    out = tmp_path / "out.csv"
    assert run_cli(inp, out, min_count=3).returncode == 0
    keys = [(r["level"], r["service"]) for r in read_summary(out)]
    assert ("WARN", "db") in keys and ("INFO", "api") not in keys


def test_output_flag_writes_to_custom_path(tmp_path):
    custom = tmp_path / "subdir" / "out.csv"
    custom.parent.mkdir(parents=True)
    result = run_cli(FIXTURES / "basic_events.csv", custom)
    assert result.returncode == 0 and custom.exists() and len(read_summary(custom)) > 0
