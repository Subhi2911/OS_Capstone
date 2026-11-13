# OS Resource-Management Simulator (Python + Bash)

One integrated application simulating CPU scheduling, memory management, deadlock avoidance and disk scheduling,
with a Bash front-end/host probe, input validation, activity logging, tests, tables and charts.

## Architecture
```
run.sh (Bash: menu|demo|test|sysinfo|clean)
  └─ python3 -m osim  (osim/main.py: menu + batch)
       ├─ scheduler.py  FCFS, SJF, SRTF, Priority, Round Robin
       ├─ memory.py     FIFO/LRU/OPT paging; First/Best/Worst fit
       ├─ deadlock.py   Banker's safety + resource-request
       ├─ storage.py    FCFS, SSTF, SCAN, C-SCAN, LOOK
       ├─ system.py  ──► scripts/sysinfo.sh (live /proc data via Bash)
       ├─ report.py     text tables, matplotlib charts, results.json
       └─ common.py     validation (InputError), logging, JSON loader
data/sample_input.json -> outputs/*.png, results.json, traces ; logs/activity.log
```
Data design: processes are dicts `{pid, arrival, burst, priority}`; matrices are lists of int lists; every module
returns a plain dict (table rows, metrics, trace) so report.py and tests consume results uniformly.

## Run
```
pip install matplotlib        # only dependency (Python 3.8+, Linux/macOS/WSL)
chmod +x run.sh
bash run.sh demo      # all modules, charts, trace -> outputs/
bash run.sh           # interactive menu (options 1-7)
bash run.sh test      # 30 unit/integration tests
python3 -m osim --all --input my.json   # custom dataset (same schema as data/sample_input.json)
```
Exit codes: 0 ok, 1 unexpected failure, 2 bad input.

## Validation / reliability
Rejects: non-integer, negative or zero burst, duplicate PIDs, empty lists, zero frames, quantum < 1, ragged/negative
Banker matrices, allocation > max, track outside disk, unknown algorithm/direction, missing/malformed JSON.
Every action and error goes to `logs/activity.log`.

## Deliverables map
source `osim/`, `scripts/` | sample input `data/` | traces `outputs/sample_output_trace.txt`, `error_handling_trace.txt`,
`test_results.txt` | charts `outputs/*.png` | screenshots `screenshots/` | report `REPORT.md` | tests `tests/`.


## Windows / Git Bash troubleshooting
- Open Git Bash first, `cd` into the folder, then run `bash run.sh demo` (double-clicking closes the window on any error).
- "bad interpreter" / `\r` errors: convert line endings: `sed -i 's/\r$//' run.sh scripts/sysinfo.sh`
- "Python not found": install Python 3 from python.org with "Add to PATH"; the script tries python3, python, py.
- Option 5 (host snapshot) shows `n/a` for memory/load on Git Bash because it has no `/proc`; it is full on Linux/WSL.

Submiited by Subhasmita Mishra
Roll Number: 2401360011