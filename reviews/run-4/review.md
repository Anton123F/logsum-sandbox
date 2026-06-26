# Review — run-4
Reviewer: engineering agent
Date: 2026-06-26
Source: `src/logsum.py` reviewed against `spec.md`
Delta since run-3: skill infrastructure added (SKILL.md updated, EVAL.md, REFERENCE.md created); no production code changes.

---

## Lens 1 — Correctness

No production code changes since run-3. All 15 spec ACs verified and passing.

| AC | Behaviour | Status |
|----|-----------|--------|
| Grouping by `(level, service)` after normalisation | `groups.setdefault(key, ...)` where `key = (_normalise_level(...), _normalise_service(...))` | ✅ |
| level: strip + uppercase + collapse internal whitespace | `" ".join(raw.split()).upper()` | ✅ |
| service: strip + lowercase + collapse internal whitespace | `" ".join(raw.split()).lower()` | ✅ |
| Empty level → `"UNKNOWN"` | `return s if s else "UNKNOWN"` | ✅ |
| Empty service → `"unknown"` | `return s if s else "unknown"` | ✅ |
| Malformed/missing timestamp → skip row + stderr WARN with row number | `print(f"WARN: skipped row {row_num} — bad timestamp", file=sys.stderr)` | ✅ |
| Header-only input → empty output, exit 0 | Empty `groups` dict → empty CSV written | ✅ |
| Missing required column → exit 1 + column name | Checks `("level", "service", "message")` | ✅ |
| File not found → exit 1 + message | `if not p.exists(): print(...)` | ✅ |
| Duplicate header → exit 1 | `seen` set check before required-column check | ✅ |
| `--min-count N` filter (inclusive) | `if stats["count"] >= min_count` | ✅ |
| Output sorted level ASC, service ASC | `sorted(groups.items())` (tuple sort) | ✅ |
| `first_seen` = min timestamp, `last_seen` = max timestamp | Lexicographic ISO 8601 compare | ✅ |
| `--output` flag honoured | `output_path` argument threaded through | ✅ |
| Extra columns ignored | `csv.DictReader` — only named keys accessed | ✅ |

**Finding:** none.

---

## Lens 2 — Security

No network calls, no credentials, no shell invocations. `Path.open()` and `open()` are safe.

**Finding (unchanged):** Output path not validated — non-existent parent directory raises unhandled `FileNotFoundError`. Not a security issue. Not blocking.

---

## Lens 3 — Performance

Single-pass O(n) read; O(g log g) sort on groups. Acceptable for CSV files.

**Finding (unchanged):** `dict.setdefault` constructs default dict eagerly on every row. Minor; documented in `refactor-notes.md`. Not blocking.

---

## Lens 4 — Maintainability

- Functions small and single-purpose. ✅
- Type hints present. ✅
- No dead code in `src/logsum.py`. ✅
- Skill infrastructure improved this run: Reserved Decisions + escalation triggers in SKILL.md; EVAL.md rubric; REFERENCE.md context pack. ✅
- `src/main.py` still present as stale stub — deletion pending human approval. ⚠️

**Finding:** `src/main.py` remains. Recommend deletion PR after human approval.

---

## Lens 5 — Error handling

| Error path | Spec requirement | Code behaviour | Status |
|------------|-----------------|----------------|--------|
| File not found | Exit 1 + "not found" | ✅ clean | ✅ |
| Duplicate header | Exit 1 + "duplicate column" | ✅ clean | ✅ |
| Missing required column | Exit 1 + column name | ✅ clean | ✅ |
| Malformed/missing timestamp | Skip row + WARN to stderr | ✅ warning emitted | ✅ |
| Output dir does not exist | Not in spec | Unhandled `FileNotFoundError` | ⚠️ |
| UTF-8 BOM in input | Not in spec | All rows silently skipped | ⚠️ |
| `--min-count 0` or negative | Not in spec | All groups pass — silent no-op | ⚠️ |

**Finding (non-blocking, unchanged):** Three out-of-spec edge cases. All outside spec scope.

---

## Lens 6 — Test coverage

| AC | Description | Test(s) | Tier |
|----|-------------|---------|------|
| AC-1 | Grouping | `test_basic_grouping` | B |
| AC-2a | Leading/trailing whitespace + case | `test_normalisation_merges_case_and_whitespace_variants` | B |
| AC-2b | Internal whitespace collapse | `test_internal_whitespace_collapsed_in_level/service` | B |
| AC-3a | Empty level → UNKNOWN | `test_empty_level_becomes_UNKNOWN` | B |
| AC-3b | Empty service → unknown | `test_empty_service_becomes_unknown` | B |
| AC-4 | Malformed timestamp skip + WARN | `test_malformed_timestamp_row_skipped_with_stderr_warning` | B |
| AC-5 | Header-only input → empty output, exit 0 | `test_header_only_input_writes_empty_summary` | B |
| AC-6 | Missing required column → exit 1 | `test_missing_required_column_exits_1` | B |
| AC-7 | File not found → exit 1 | `test_input_file_not_found_exits_1` | B |
| AC-8 | Duplicate header → exit 1 | `test_duplicate_header_exits_1` | B |
| AC-9 | `--min-count` filtering (4 boundary tests) | `test_min_count_*` | B |
| AC-10 | Sort order level ASC, service ASC | `test_output_sorted_level_then_service_asc` | B |
| AC-11 | `first_seen` / `last_seen` correctness | `test_first_seen_and_last_seen_are_correct`, `test_first_seen_equals_last_seen_for_single_row_group` | B |
| AC-12 | `--output` flag | `test_cli_output_flag_writes_to_custom_path` | B |
| AC-13 | Extra columns ignored | `test_extra_columns_ignored_silently` | B |

**Totals:** 20 tests, 15 ACs, 0 uncovered. All pass. Tier B.

**Finding:** none.

---

## Lens 7 — Spec compliance

- All functional behaviours match spec. ✅
- Spec CLI says `python -m src.main`; real entry point is `src.logsum`. Signed off — not changed. CLAUDE.md carries corrected invocation. ⚠️ (known)
- `message` required-or-not ambiguity persists. Cold gap documented. ⚠️ (known)

**Finding (non-blocking, unchanged):** Two spec wording ambiguities awaiting spec owner sign-off.

---

## Adversarial pass

| Scenario | Result |
|----------|--------|
| All rows have empty level and service | One `UNKNOWN/unknown` group. Correct. |
| `timestamp` column entirely absent | All rows skipped; empty output, exit 0. Implicit — acceptable. |
| Windows CRLF line endings | `newline=""` on open handles correctly. ✅ |
| UTF-8 BOM input | All rows silently skipped. Non-clean. Noted Lens 5. |
| `--output` path in non-existent directory | Unhandled `FileNotFoundError`. Noted Lens 5. |
| `--min-count 0` or `-1` | All groups included. Undocumented but harmless. |
| CSV with only whitespace in every level/service cell | All map to `UNKNOWN/unknown`. Valid. |
| Single row file | `first_seen == last_seen`. Correct. ✅ |
| `--min-count` equal to exact group count | Group included (`>=`). Correct per spec. ✅ |
| Very large `--min-count` value | All groups filtered, empty output, exit 0. Valid. |

**Security-class findings:** none. No escalation required.

---

## Verdict

**PASS** — implementation fully matches spec; 15 ACs covered by 20 passing tests (Tier B); no blocking findings. Three non-blocking out-of-spec edge cases and two spec ambiguities carry forward — all documented, awaiting spec owner decision.
