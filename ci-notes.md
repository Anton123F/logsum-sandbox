# CI Notes

## Red run
URL: https://github.com/Anton123F/logsum-sandbox/actions/runs/27868600167
Failure: ruff F401 — unused `pytest` import in tests/test_logsum.py
Fix: removed the import (it was never used, no test logic changed)

## Green run
URL: https://github.com/Anton123F/logsum-sandbox/actions/runs/27868696286
ruff: passed
pytest: 8 passed
