# K 5.W.9 - By-hand vs by-agent comparison

## What both produced

Both the supervised chain and the agent replay produced:

- `src/logsum.py` — identical logic: normalisation, grouping, all eight edge cases from spec, `--input`/`--output`/`--min-count` flags, exit codes
- `tests/test_logsum.py` — 12 tests each, all passing, covering the same core spec behaviours
- `.github/workflows/ci.yml` — Python 3.11, `ruff check .`, `pytest -v`, triggers on push and pull_request
- A refactor of the `setdefault` pattern (both arrived at the same final form)
- A provenance/documentation artefact

The implementations are so close that a line-by-line diff shows only cosmetic differences: variable name `col` vs `required` in the required-column loop, `list(reader.fieldnames or [])` vs `reader.fieldnames or []`.

---

## Where the agent saved time

**Speed.** The agent produced all five artefacts (implementation, tests, CI, refactor, provenance) in a single pass in under 5 minutes. The supervised chain took multiple sessions across K 5.W.2–8.

**No ruff failure.** The supervised chain hit a red CI run (unused `pytest` import, ci-notes.md red run URL). The agent never imported `pytest` unnecessarily, so the first push would have been green.

**Covered two edge cases the supervised chain missed in tests:**
- `test_empty_service_becomes_unknown` — supervised tested empty level → UNKNOWN but never wrote a test for empty service → "unknown"
- `test_duplicate_column_exits_1` — the spec lists duplicate column as an exit-1 case; supervised chain never wrote a test for it

---

## Where the agent went wrong or shorter

**Missed three `--min-count` tests the supervised chain wrote:**
- `test_min_count_default_keeps_all_groups` — verifies that running with no flag produces identical output to `--min-count 1`. The agent assumed this was covered by other tests.
- `test_min_count_filters_all_groups` — verifies the output is empty (not an error) when all groups are below threshold. The agent only tested partial filtering.
These are boundary conditions that matter: the first guards against a flag-parsing regression, the second guards against an off-by-one that turns an empty result into a crash.

**Provenance is shallow.** The supervised chain produced `questions.md` with cited line numbers, a verification table, and reasoned "could not verify" entries. The agent provenance note lists decisions but has no line citations and no systematic verification pass. A reviewer reading the agent note cannot tell whether the agent actually checked each claim.

**Refactor scope was narrower.** The supervised chain documented two distinct refactors with a risk table for each (setdefault + sorted(groups.items()) sort simplification). The agent treated the second change as part of the initial implementation, so only one explicit refactor was recorded. The refactor-notes.md artefact from the supervised chain would be absent from the agent replay.

---

## What the agent did better

**Symmetric edge case coverage.** The agent noticed that empty `service` is a mirror of empty `level` and wrote the test. The supervised chain wrote one and forgot the other, which means a regression in `_normalise_service` would be invisible to the supervised test suite.

**No ruff noise.** The agent wrote clean imports from the start, avoiding the false-start that cost an extra CI run in the supervised chain.

**Consistent naming.** The agent test names are shorter and uniform (e.g. `test_bad_timestamp_skipped_with_warning`). The supervised names vary in length and style (`test_malformed_timestamp_row_skipped_with_stderr_warning`).

---

## What I learned about supervised vs async

**Supervised work builds understanding; async work produces artefacts.**
Each step of K 5.W.2–8 forced a decision: what goes in the spec, which edge case matters, why this refactor. The agent skipped all of that deliberation. The code is nearly identical, but only one of us can explain *why* `setdefault` has an eager-evaluation cost on high-cardinality paths (from refactor-notes.md).

**Green tests are not the same as correct coverage.**
Both suites pass. But the supervised suite caught two min-count boundary cases the agent missed. If the `--min-count` logic had a bug at zero or at "all filtered", the agent's suite would not catch it. The lesson: when you supervise, you think about what *could* go wrong; when you delegate, the agent covers what it *remembers* from the spec.

**The provenance gap is the real risk.**
The agent produced working code but thin provenance. If someone inherits this codebase six months from now and asks "why is `timestamp` not in the required-column check?", the supervised chain has a documented answer (questions.md, spec edge case table). The agent replay has a one-line note. Async work produces less institutional memory.

**Async is safe when the spec is airtight and the reviewer is thorough.**
Every delta between the two outputs traces back to either (a) an underspecified case in spec.md or (b) the reviewer not checking beyond "tests pass". The agent did nothing wrong; it read the spec faithfully. The gaps are spec gaps and review gaps.

---

## What I would do differently next time

1. **Review agent tests against the spec edge-case table row by row, not just "does it pass".** I would have caught the missing `test_min_count_filters_all_groups` in 30 seconds with a checklist.

2. **Ask the agent for a provenance note with line citations before accepting the output.** Shallow provenance is the biggest long-term cost of async work.

3. **Use async for the first draft, supervised for the boundary cases.** The agent is faster and gets the happy path right. Boundary conditions (empty output, exact threshold, symmetric normalisation) are where supervision adds value. A hybrid — agent writes the scaffold, human reviews and adds the missing boundary tests — would have been faster than supervised and more complete than async.

4. **Check both directions of symmetric edge cases.** If the spec says "empty level → UNKNOWN" and "empty service → unknown", write tests for both. The supervised chain missed one; the agent caught it only by accident.
