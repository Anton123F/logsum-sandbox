# Context bundle — task-1
Generated: 2026-06-24

---

## Hot layer (`CLAUDE.md`)

Updated in this session. Two factual errors corrected:

| Was | Now |
|-----|-----|
| "prints a summary to stdout" | "writes a summary to `summary.csv` (default) or `--output` path" |
| no CLI invocation shown | `python -m src.logsum` documented |

Added a **Stale files** section noting `src/main.py` and `data/events.csv` are legacy.

---

## Warm layer — `spec.md` verification

Checked every spec claim against the current `src/logsum.py` implementation.

| Spec claim | Status | Note |
|------------|--------|------|
| CLI: `python -m src.main` | ❌ Wrong | Real module is `src.logsum`; `src/main.py` is a stale stub |
| Required columns: level, service, message, timestamp | ✅ | Code checks level/service/message; timestamp triggers row-skip (not file error) |
| level normalised: strip + uppercase + collapse internal whitespace | ✅ | `_normalise_level` in logsum.py |
| service normalised: strip + lowercase + collapse internal whitespace | ✅ | `_normalise_service` in logsum.py |
| Empty level → "UNKNOWN" | ✅ | |
| Empty service → "unknown" | ✅ | |
| Malformed timestamp → skip row + stderr WARN with row number | ✅ | Fixed in last CI green run |
| Header-only input → empty output, exit 0 | ✅ | |
| Missing required column → exit 1 + column name in message | ✅ | |
| Input file not found → exit 1 + "not found" in message | ✅ | |
| Duplicate header → exit 1 + "duplicate column" in message | ✅ | |
| `--min-count N` filters groups below N; default 1 | ✅ | |
| Output sorted level ASC, service ASC | ✅ | `sorted(groups.items())` |
| Output: count, first_seen, last_seen | ✅ | |
| `--output` flag honoured | ✅ | |

**One warm-layer discrepancy found:** spec CLI section still says `python -m src.main`.
The spec is signed-off — do not change it without explicit approval. The CLAUDE.md now
carries the corrected invocation as the authoritative reference.

---

## Cold gaps (not captured anywhere in docs/spec)

| # | Gap | Risk |
|---|-----|------|
| 1 | `src/main.py` purpose/status not documented | An agent or contributor may edit or invoke the wrong file |
| 2 | `data/events.csv` schema mismatch not noted | Running the CLI against the default path silently produces wrong results |
| 3 | Behaviour when `timestamp` column is entirely **absent** from headers is not specified (implicit: every row is skipped, exit 0, empty output) | Surprising UX; could mask schema errors |
| 4 | `refactor-notes.md` notes a performance issue with eager `dict.setdefault` argument evaluation — not referenced from spec, CLAUDE.md, or any ADR | Invisible tech-debt entry |
| 5 | No documented behaviour for `message` column being absent (code exits 1 via required-column check, but spec edge-case table only says "not `timestamp`" for missing columns, leaving ambiguity about whether `message` is truly required) | Test gap; spec could be read as message being optional |

**Recommended follow-ups (do not implement without human approval):**
- Add a spec note or ADR clarifying whether `message` is a required column
- Clarify behaviour for fully-absent `timestamp` column
- Mark `src/main.py` and `data/events.csv` as deprecated in repo (e.g., a comment or deletion PR)
