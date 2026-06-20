import csv
import tempfile
from pathlib import Path

from src.main import summarise


def make_csv(rows: list[dict]) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
    writer = csv.DictWriter(f, fieldnames=["timestamp", "event_type", "user_id", "duration_ms"])
    writer.writeheader()
    writer.writerows(rows)
    f.close()
    return f.name


def test_summarise_runs(capsys):
    path = make_csv([
        {"timestamp": "2024-01-01T00:00:00Z", "event_type": "login", "user_id": "u1", "duration_ms": "100"},
        {"timestamp": "2024-01-01T00:01:00Z", "event_type": "click", "user_id": "u1", "duration_ms": "200"},
    ])
    summarise(path)
    out = capsys.readouterr().out
    assert "Total events : 2" in out
    assert "login" in out
