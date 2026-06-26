# logsum-sandbox

## Project Context
Tiny CLI (`python -m src.logsum`) that reads `data/events.csv`, groups events
by (level, service), and writes a summary to `summary.csv` (default) or the
path given by `--output`.
Synthetic data only — no real user data ever enters this repo.

## Stale files (do not use)
- `src/main.py` — old stub with a different schema (event_type/duration_ms); superseded by `src/logsum.py`
- `data/events.csv` — legacy schema (event_type/user_id/duration_ms); does not match the current spec

## Active data files
- `data/sample_events.csv` — correct-schema sample (timestamp/level/service/message); safe for manual testing
- `tests/fixtures/basic_events.csv` — minimal fixture used by `test_basic_grouping`

## Conventions
- Source code → `src/`
- Tests → `tests/`
- Data files → `data/`

## Utilities to Prefer
- Python 3.11+ standard library only (no third-party packages)
- `ruff` for linting — install with `pip install ruff` if not present
- `pytest` for tests

## Escalation Gates
- Stop and ask before adding any dependency
- Use synthetic data only — never real user data
- Never overwrite `spec.md` after sign-off without explicit approval
