## Removed by AI in the refactor

### Hunk — timestamp validation block (lines 43–50)

```python
ts = row.get("timestamp", "").strip()
try:
    if not ts:
        raise ValueError
    datetime.fromisoformat(ts.replace("Z", "+00:00"))
except ValueError:
    print(f"WARN: skipped row {row_num} — bad timestamp", file=sys.stderr)
    continue
```

**Replaced with:**
```python
ts = _valid_ts(row.get("timestamp", ""))
if ts is None:
    print(f"WARN: skipped row {row_num} — bad timestamp", file=sys.stderr)
    continue
```

Where `_valid_ts` is a new helper:
```python
def _valid_ts(raw: str) -> str | None:
    ts = raw.strip()
    if not ts:
        return None
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return ts
    except ValueError:
        return None
```

#### Removed items and their decisions

| Line | What it was | AI reason | My decision |
|------|-------------|-----------|-------------|
| `if not ts: raise ValueError` | Guard: empty string triggers skip | Replaced by `if not ts: return None` in helper | **Keep removed** — empty string still returns None, still triggers warning and continue. Behaviour identical. |
| `datetime.fromisoformat(ts.replace("Z", "+00:00"))` | Validation call inside try block | Moved into helper | **Keep removed** — same call, same ValueError caught, same result. |
| `ts = row.get(...).strip()` | Strip done inline before try | `.strip()` now done inside helper, helper returns stripped value | **Keep removed** — `ts` in the loop now holds the already-stripped, validated string. No behaviour change. |

