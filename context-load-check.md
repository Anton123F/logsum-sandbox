# Context Load Check

**File loaded:** `CLAUDE.md` (logsum-sandbox project root)

## Project Context
Tiny CLI that reads `data/events.csv` and prints a summary to stdout. Synthetic data only — no real user data ever enters this repo.

## Conventions
Source in `src/`, tests in `tests/`, data files in `data/`.

## Utilities to Prefer
Python 3.11 standard library only. `ruff` for linting, `pytest` for tests.

## Escalation Gates
- Stop and ask before adding any dependency
- Use synthetic data only — never real user data
- Never overwrite `spec.md` after sign-off without explicit approval
