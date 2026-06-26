# EVAL.md — Engineering skill grading rubric

Each row is a criterion the agent's own output is graded on.
Run against two inputs and record a pass/fail verdict per input.

**Input A:** `spec.md` + artifacts from before run-1 fix (no `test_spec_independent.py`, no tier entry)
**Input B:** `spec.md` + current run-3 artifacts (`test_spec_independent.py` present, Tier B recorded)

---

| # | Eval | Test input | Pass/fail signal | Input A | Input B |
|---|------|------------|------------------|---------|---------|
| 1 | Tests are independent + tier recorded | `spec.md` (15 ACs) | Tier entry present in test file header; tests not authored in the implementation session | **FAIL** — no `test_spec_independent.py`; tier field blank; tests written inline with impl | **PASS** — `tests/test_spec_independent.py` header declares Tier B; session log confirms separate generation step |
| 2 | Every AC covered by ≥1 test citing it | `spec.md` | Count of ACs with zero covering tests = 0 | **FAIL** — AC-3b, AC-2b, AC-8, AC-10, AC-11, AC-13 had no dedicated test before `test_spec_independent.py` existed | **PASS** — all 15 ACs mapped in `reviews/run-3/review.md` Lens 6; 0 uncovered |
| 3 | All 7 lenses run + adversarial pass present | `reviews/run-3/review.md` | Lens heading count = 7; adversarial section present; 0 lens bodies blank | N/A (no review file in Input A state) | **PASS** — 7 lens headings confirmed; adversarial pass section present; every lens has a named finding or explicit "none found" |
| 4 | Provenance block complete — all 4 links present | `sessions/run-3/pr-body.md` | Spec + session-log + tests + review all present in provenance table | N/A (no PR body in Input A state) | **PASS** — provenance table has 4 rows: spec, session-log, independent tests (with tier), review |

---

## Fail → Pass trace (Evals 1 & 2)

**Before (Input A state):**
- `tests/test_logsum.py` was the only test file
- No isolation tier recorded anywhere
- ACs AC-3b, AC-2b, AC-8, AC-10, AC-11, AC-13 had zero covering tests

**Fix applied (run-1):**
- Generated `tests/test_spec_independent.py` in a separate session seeded from `spec.md` only
- Added tier declaration in file header: `Isolation tier: B`
- Covered all 6 previously-uncovered ACs with explicit AC citations in docstrings

**After (Input B state):**
- Eval 1: PASS — tier entry present, generated outside impl session
- Eval 2: PASS — 0 ACs uncovered

---

## Grading instructions

Run this rubric after every evidence-chain run before the PR opens:

1. Open `tests/test_spec_independent.py` — verify tier entry in header and AC citations in docstrings (Eval 1, 2).
2. Open `reviews/<run>/review.md` — count lens headings; confirm adversarial section; check no lens body is blank (Eval 3).
3. Open `sessions/<run>/pr-body.md` — count provenance table rows; must be exactly 4 (Eval 4).
4. Record verdicts in the session log escalation section. Any FAIL blocks the PR.
