## first run failed (https://github.com/Anton123F/logsum-sandbox/actions/runs/28007065370/job/82891365428)
F401 [*] `pathlib.Path` imported but unused
 --> tests/test_main.py:3:21
  |
1 | import csv
2 | import tempfile
3 | from pathlib import Path
  |                     ^^^^
4 |
5 | from src.main import summarise
  |
help: Remove unused import: `pathlib.Path`

Found 1 error.
[*] 1 fixable with the `--fix` option.
## second failed (https://github.com/Anton123F/logsum-sandbox/actions/runs/28007239282)
unused config from brevious branch cause an error
## third attemp success (https://github.com/Anton123F/logsum-sandbox/actions/runs/28007388176)
