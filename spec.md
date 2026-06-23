# logsum-sandbox — Spec

## Goal
CLI tool that reads `events.csv`, groups events by (level, service), and writes
a summary to `summary.csv`. Produces a human-auditable aggregate without any
third-party dependencies.

## Inputs
File: `data/events.csv`
Required columns (order-independent, header row mandatory):

| Column      | Type   | Notes                        |
|-------------|--------|------------------------------|
| `timestamp` | string | ISO 8601, e.g. `2024-01-15T08:01:00Z` |
| `level`     | string | e.g. `INFO`, `WARN`, `ERROR` |
| `service`   | string | e.g. `auth`, `payments`      |
| `message`   | string | Free text, not used in grouping |

## Outputs
File: `summary.csv` (default) or path set by `--output` flag.
One row per unique (level, service) group, columns:

| Column       | Type    | Notes                              |
|--------------|---------|------------------------------------|
| `level`      | string  | Normalised (see below)             |
| `service`    | string  | Normalised (see below)             |
| `count`      | integer | Number of matching rows            |
| `first_seen` | string  | ISO 8601 timestamp of earliest row |
| `last_seen`  | string  | ISO 8601 timestamp of latest row   |

Rows sorted by `level` ASC, then `service` ASC.

## Normalisation Rules
- `level`: strip leading/trailing whitespace, convert to uppercase.
- `service`: strip leading/trailing whitespace, convert to lowercase.
- Both fields: collapse internal runs of whitespace to a single space.

## Grouping Rule
Group key = (`level`, `service`) after normalisation.
`message` and `timestamp` are not part of the key.

## Aggregation
For each group:
- `count` — total rows in group.
- `first_seen` — minimum `timestamp` value (lexicographic ISO 8601 sort is correct).
- `last_seen` — maximum `timestamp` value.

## Edge Cases

| Situation | Behaviour |
|-----------|-----------|
| `level` is empty or whitespace-only | Treat as `"UNKNOWN"` |
| `service` is empty or whitespace-only | Treat as `"unknown"` |
| `timestamp` is malformed or missing | Skip row; print warning to stderr: `WARN: skipped row <N> — bad timestamp` |
| Extra columns in CSV | Ignore silently |
| Missing required column (not `timestamp`) | Exit 1 with message: `ERROR: missing required column '<name>'` |
| Input file is empty (no rows, header only) | Write header-only `summary.csv`; exit 0 |
| Input file does not exist | Exit 1 with message: `ERROR: input file not found: <path>` |
| Duplicate header names in CSV | Exit 1 with message: `ERROR: duplicate column '<name>'` |

## CLI

```
python -m src.main [--input PATH] [--output PATH]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | `data/events.csv` | Path to input CSV |
| `--output` | `summary.csv` | Path to output CSV |

Exit codes:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Any error (missing file, bad column, unhandled exception) |

Warnings go to **stderr**. Normal output (progress, summary line count) goes to **stdout**.

## Implementation notes
- The spec lists `timestamp` in the required-columns table but the edge-case table says "Missing required column (not timestamp)" — so `timestamp` is intentionally excluded from the exit-1 check; a missing timestamp column causes every row to be skipped with warnings rather than an immediate error exit.

## Out of Scope
- Filtering by date range, level, or service
- Real-time or streaming input
- Database or JSON output formats
- Deduplication of identical rows
- Internationalisation or locale-aware sorting
- Any third-party package (stdlib only)
