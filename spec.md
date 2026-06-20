# logsum-sandbox — Spec

## Goal
CLI tool that reads a CSV of synthetic events and prints a human-readable summary.

## Inputs
- `data/events.csv` — columns: `timestamp`, `event_type`, `user_id`, `duration_ms`

## Outputs
Printed to stdout:
- Total event count
- Average duration in ms
- Per-type breakdown (sorted by frequency)

## Constraints
- Python 3.11 standard library only (no third-party packages)
- Synthetic data only
