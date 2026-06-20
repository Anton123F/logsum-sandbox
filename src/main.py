import csv
import sys
from collections import Counter
from pathlib import Path


def summarise(path: str) -> None:
    file = Path(path)
    if not file.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    with file.open(newline="") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    counts = Counter(r["event_type"] for r in rows)
    avg_duration = sum(int(r["duration_ms"]) for r in rows) / total if total else 0

    print(f"Total events : {total}")
    print(f"Avg duration : {avg_duration:.1f} ms")
    print("By type:")
    for event, count in counts.most_common():
        print(f"  {event:<12} {count}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "data/events.csv"
    summarise(target)
