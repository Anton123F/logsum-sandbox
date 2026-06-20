import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path


def _normalise_level(raw: str) -> str:
    s = " ".join(raw.split()).upper()
    return s if s else "UNKNOWN"


def _normalise_service(raw: str) -> str:
    s = " ".join(raw.split()).lower()
    return s if s else "unknown"


def run(input_path: str, output_path: str) -> int:
    p = Path(input_path)
    if not p.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        return 1

    with p.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        seen: set[str] = set()
        for h in headers:
            if h in seen:
                print(f"ERROR: duplicate column '{h}'", file=sys.stderr)
                return 1
            seen.add(h)

        for required in ("level", "service", "message"):
            if required not in headers:
                print(f"ERROR: missing required column '{required}'", file=sys.stderr)
                return 1

        groups: dict[tuple[str, str], dict] = {}

        for row_num, row in enumerate(reader, start=2):
            ts = row.get("timestamp", "").strip()
            try:
                if not ts:
                    raise ValueError
                datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                print(f"WARN: skipped row {row_num} — bad timestamp", file=sys.stderr)
                continue

            level = _normalise_level(row.get("level", ""))
            service = _normalise_service(row.get("service", ""))
            key = (level, service)

            if key not in groups:
                groups[key] = {"count": 0, "first_seen": ts, "last_seen": ts}
            g = groups[key]
            g["count"] += 1
            if ts < g["first_seen"]:
                g["first_seen"] = ts
            if ts > g["last_seen"]:
                g["last_seen"] = ts

    out_rows = sorted(
        [{"level": k[0], "service": k[1], **v} for k, v in groups.items()],
        key=lambda r: (r["level"], r["service"]),
    )

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["level", "service", "count", "first_seen", "last_seen"])
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Written {len(out_rows)} group(s) to {output_path}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/events.csv")
    ap.add_argument("--output", default="summary.csv")
    args = ap.parse_args()
    sys.exit(run(args.input, args.output))
