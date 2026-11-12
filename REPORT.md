# Concise Report — OS Resource-Management Simulator

## 1. Problem and design (Phase 1)
Operating systems arbitrate four scarce resources: CPU, memory, resources prone to deadlock, and disk bandwidth.
The project models each as a module with a common pattern: validate input → simulate → return metrics → report.
Python holds the logic; Bash supplies the launcher and a live host snapshot (`/proc`) so the simulator is tied to the real OS.
Plan: design (data structures, flow) → modules → comparison → tests/logging → documentation.

## 2. Modules (Phase 2)
Five modules (scheduling, memory, deadlock, storage, reporting) plus Bash bridge; menu and batch mode share the same functions.

## 3. Results on the sample dataset (Phase 3)
**CPU scheduling** (5 processes, quantum 2):

| Algo | Avg WT | Avg TAT | Avg RT | Ctx switches |
|---|---|---|---|---|
| FCFS | 9.8 | 15.6 | 9.8 | 4 |
| SJF | 7.4 | 13.2 | 7.4 | 4 |
| SRTF | **6.4** | **12.2** | 4.0 | 6 |
| Priority | 7.4 | 13.2 | 7.4 | 4 |
| RR | 13.8 | 19.6 | **2.8** | 14 |

SRTF minimises waiting/turnaround; RR gives best response time but the worst waiting and most context switches
(interactive vs batch trade-off). FCFS suffers the convoy effect (long P1 first).

**Paging** (20-ref string, 3 frames): FIFO 15, LRU 12, OPT 9 faults. OPT is the lower bound; LRU approximates it.
Belady's anomaly reproduced: FIFO faults rise 9→10 going from 3→4 frames; LRU never does (stack algorithm).

**Contiguous allocation** (partitions 100/500/200/300/600; requests 212/417/112/426): Best-fit places all four;
First-fit fails the 426 request, showing that fit strategy affects external fragmentation.

**Banker's algorithm**: initial state safe, sequence P1→P3→P4→P0→P2; request P1(1,0,2) granted; the textbook follow-up
request P0(0,2,0) is denied because it leads to an unsafe state (covered by tests).

**Disk scheduling** (head 53, 200 tracks): FCFS 640, SSTF 236, LOOK 299, SCAN 331, C-SCAN 382 tracks.
SSTF is shortest here but can starve far requests; LOOK/SCAN bound waiting; C-SCAN is more uniform at higher distance
(wrap-around counted as movement).

Charts: `gantt.png`, `scheduling_comparison.png`, `page_faults.png`, `belady.png`, `allocation.png`, `disk_seek.png`.

## 4. Testing (Phase 4)
30 tests: known textbook answers, boundary cases (1 frame, single request, idle CPU gap), invalid input (zero burst,
duplicate PID, ragged matrix, out-of-range track, bad quantum), Bash bridge and CLI exit codes. All pass (`outputs/test_results.txt`).
Failure of an earlier draft test (wrong assumption about the Banker follow-up state) was corrected by using the textbook state.

## 5. Limitations
Discrete integer time; no I/O bursts or process arrival from live system; C-SCAN counts the wrap seek; fragmentation is
reported as total free space, not per-hole. Extensions: multilevel queue, segmentation, file-allocation methods.
