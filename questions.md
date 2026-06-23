# Q&A — logsum-sandbox

---

## Q1: Where is the grouping rule?

**Files read:** `src/logsum.py`, `spec.md`

**Answer:**
Each CSV row is assigned a key of `(normalised_level, normalised_service)`. Rows that share the same key are merged into one group. The group accumulates a count, a `first_seen`, and a `last_seen` timestamp. The key is built inside the row-processing loop and groups are stored in a plain dict keyed by that tuple.

**Citations:**
- `spec.md:38-40` — spec definition: "Group key = (level, service) after normalisation. message and timestamp are not part of the key."
- `src/logsum.py:51` — groups dict declared: `groups: dict[tuple[str, str], dict] = {}`
- `src/logsum.py:59-62` — key construction: `key = (_normalise_level(...), _normalise_service(...))`
- `src/logsum.py:63-68` — group accumulation: `setdefault`, `count += 1`, min/max timestamps

**Could not verify:** Nothing — all claims have direct code backing.

---

## Q2: How is missing level handled?

**Files read:** `src/logsum.py`, `spec.md`

**Answer:**
Two distinct cases:

1. **`level` column present but empty or whitespace-only:** `_normalise_level` returns `"UNKNOWN"`. This happens because `.split()` on a whitespace-only string returns an empty list, so `" ".join([])` produces `""`, and the `if s else "UNKNOWN"` fallback kicks in. The row is not skipped — it is grouped under `("UNKNOWN", service)`.

2. **`level` column entirely absent from the CSV header:** The required-column check at lines 46–49 catches this before any row is processed and exits with `ERROR: missing required column 'level'`. `_normalise_level` is never called.

**Citations:**
- `src/logsum.py:8-10` — `_normalise_level`: `s = " ".join(raw.split()).upper()` then `return s if s else "UNKNOWN"`
- `src/logsum.py:60` — called per row: `_normalise_level(row.get("level", ""))`
- `src/logsum.py:46-49` — required column check exits before normalisation if column is absent
- `spec.md:52` — edge case: "`level` is empty or whitespace-only → Treat as `"UNKNOWN"`"

**Could not verify:** Nothing — both code paths confirmed.

---

## Q3: How do I run tests and CI locally?

**Files read:** `.github/workflows/ci.yml`, `CLAUDE.md`

**Answer:**
To run tests locally:
```bash
python -m pytest tests/test_logsum.py -v
```
To replicate CI locally (lint + tests):
```bash
pip install ruff pytest
ruff check .
pytest -v
```
CI runs on every push and pull request. It uses Python 3.11, installs `ruff` and `pytest`, runs `ruff check .` first, then `pytest -v`.

**Citations:**
- `CLAUDE.md` — utilities: `ruff` for linting, `pytest` for tests
- `.github/workflows/ci.yml:3` — triggers: `[push, pull_request]`
- `.github/workflows/ci.yml:12` — `python-version: "3.11"`
- `.github/workflows/ci.yml:13` — `pip install ruff pytest`
- `.github/workflows/ci.yml:14` — `ruff check .`
- `.github/workflows/ci.yml:15` — `pytest -v`

**Could not verify:** No `Readme.md` exists on this branch (`agent-replay`), so there is no documented test command there. The command above is derived from `CLAUDE.md` and CI workflow only.

---

## Verification

| Citation | Check | Verdict |
|---|---|---|
| `spec.md:38-40` — grouping rule definition | Lines 38–40 read: `## Grouping Rule`, `Group key = (level, service) after normalisation.`, `message and timestamp are not part of the key.` | **Correct** |
| `src/logsum.py:51` — groups dict declared | Line 51: `groups: dict[tuple[str, str], dict] = {}` | **Correct** |
| `src/logsum.py:59-62` — key construction | Lines 59–62: `key = (_normalise_level(row.get("level", "")), _normalise_service(row.get("service", "")))` | **Correct** |
| `src/logsum.py:63-68` — group accumulation | Lines 63–68: `setdefault`, `count += 1`, min/max on `first_seen`/`last_seen` | **Correct** |
| `src/logsum.py:8-10` — `_normalise_level` body | Lines 8–10: `def _normalise_level`, `s = " ".join(raw.split()).upper()`, `return s if s else "UNKNOWN"` | **Correct** |
| `src/logsum.py:60` — `_normalise_level` called per row | Line 60: `_normalise_level(row.get("level", ""))` | **Correct** |
| `src/logsum.py:46-49` — required column check | Lines 46–49: loop over `("level", "service", "message")`, exits on missing | **Correct** |
| `spec.md:52` — empty level edge case | Line 52: `` `level` is empty or whitespace-only | Treat as `"UNKNOWN"` `` | **Correct** |
| `.github/workflows/ci.yml:3` — CI triggers | Line 3: `on: [push, pull_request]` | **Correct** |
| `.github/workflows/ci.yml:12` — Python version | Line 12: `python-version: "3.11"` | **Correct** |
| `.github/workflows/ci.yml:13` — pip install | Line 13: `run: pip install ruff pytest` | **Correct** |
| `.github/workflows/ci.yml:14` — ruff step | Line 14: `run: ruff check .` | **Correct** |
| `.github/workflows/ci.yml:15` — pytest step | Line 15: `run: pytest -v` | **Correct** |

**Finding — spec drift on CLI entry point:**
`spec.md:64` documents the CLI as `python -m src.main` with no `--min-count` flag.
The actual implementation lives in `src/logsum.py` (not `src.main`) and adds `--min-count` at `src/logsum.py:91`.
The spec CLI section was never updated to reflect the final module name or the added flag.
No answer above is wrong because of this, but it is a verified discrepancy between spec and code.
