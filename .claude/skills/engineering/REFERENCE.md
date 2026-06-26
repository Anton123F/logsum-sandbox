# REFERENCE.md — Engineering Context Pack

Load this file when starting a new evidence-chain run.
It gives the agent real product context instead of a cold guess from training data.

---

## Hot — Rule file

`.claude/skills/engineering/SKILL.md`

Decision rules, Reserved Decisions list, Escalation triggers (5 yes/no conditions), Evals table, Run-log.
Read this first. It overrides any default engineering behaviour.

---

## Warm — Project context

**CLAUDE.md** — authoritative project index:
- Entry point: `python -m src.logsum` (not `src.main` — spec has a typo; `src/main.py` is a stale stub)
- Active source: `src/logsum.py`
- Active data: `data/sample_events.csv` (correct schema); `tests/fixtures/basic_events.csv` (test fixture)
- Stale/do-not-use: `src/main.py`, `data/events.csv`
- Runtime: Python 3.11+, stdlib only, no third-party packages
- Linter: `ruff` — install with `pip install ruff` if absent

**spec.md** — the AC source of truth:
- Signed off: Anton_Fiadotau 2026-06-20
- 15 ACs across grouping, normalisation, edge cases, CLI flags, exit codes
- Post-sign-off notes appended (lines 93–94) — analysed in run-2, no new ACs introduced
- Do not modify without explicit owner approval

**Stack:**
- Language: Python 3.13.7 (env); requires 3.11+ (spec)
- I/O: `csv.DictReader` / `csv.DictWriter`, `pathlib.Path`, `argparse`
- No database, no network, no third-party packages

---

## ADRs — Decisions that bound this feature

| # | Decision | Rationale | Status |
|---|----------|-----------|--------|
| ADR-1 | `message` column is treated as required (exit 1 if absent) | Code checks `("level", "service", "message")`; spec wording is ambiguous ("not `timestamp`"). Implementation chose required. | Open — spec owner needs to confirm |
| ADR-2 | `timestamp` column absence silently skips all rows (exit 0, empty output) | `row.get("timestamp", "")` returns `""` → row-skip path. Not a clean failure. | Open — cold gap; spec owner to decide if exit 1 is preferred |
| ADR-3 | Lexicographic ISO 8601 string comparison for `first_seen`/`last_seen` | Spec explicitly permits this ("lexicographic ISO 8601 sort is correct"). No `datetime` parse needed for aggregation. | Closed — spec-authorised |
| ADR-4 | `--min-count` filter is inclusive (`>=`) | Spec says "omit groups whose count is below N", so N itself is included. | Closed — spec-authorised |
| ADR-5 | UTF-8 BOM input not handled (`utf-8`, not `utf-8-sig`) | `\ufeff` prefix on first fieldname causes all rows to be silently skipped. Out of spec scope. | Open — cold gap; low-risk fix (`encoding="utf-8-sig"`) pending spec owner decision |

---

## NFR budgets

| Constraint | Value | Source |
|------------|-------|--------|
| Dependencies | 0 third-party packages | spec.md §Out of Scope |
| External network calls | None | spec.md §Out of Scope + SKILL.md tools declaration |
| Real user data | Never — synthetic only | CLAUDE.md §Escalation Gates |
| Spec modification | Requires explicit owner approval | CLAUDE.md §Escalation Gates |
| Output format | CSV only (no JSON, no DB) | spec.md §Out of Scope |

---

## Known cold gaps (from task-2 context bundle)

These are undocumented behaviours that affect agent decisions. Check before implementing any change near them:

| Gap | Risk | Owner action needed |
|-----|------|---------------------|
| `timestamp` column absent from headers → silent empty output | Data silently dropped | Spec owner: exit 1 or document |
| `message` required-or-not ambiguity | Contributor confusion | Spec owner: clarify |
| `--min-count 0` / negative → all groups pass | Footgun if filter semantics change | Spec owner: add validation or document |
| UTF-8 BOM → all rows silently skipped | Silent data loss | Fix: `encoding="utf-8-sig"` |
| Output path parent dir absent → unhandled `FileNotFoundError` | Non-clean exit | Spec owner: validate or document |
