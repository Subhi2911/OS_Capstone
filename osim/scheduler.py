"""CPU scheduling: FCFS, SJF, SRTF, Priority, Round Robin."""
from collections import deque
from .common import validate_processes, _int, log

ALGOS = ["FCFS", "SJF", "SRTF", "PRIORITY", "RR"]

def _compress(ticks):
    g = []
    for t, pid in enumerate(ticks):
        if g and g[-1][0] == pid:
            g[-1][2] = t + 1
        else:
            g.append([pid, t, t + 1])
    return [tuple(x) for x in g]

def _metrics(procs, finish, first):
    rows = []
    for p in procs:
        ct = finish[p["pid"]]
        tat = ct - p["arrival"]
        rows.append({"pid": p["pid"], "arrival": p["arrival"], "burst": p["burst"],
                     "completion": ct, "turnaround": tat, "waiting": tat - p["burst"],
                     "response": first[p["pid"]] - p["arrival"]})
    n = len(rows)
    avg = {k: round(sum(r[k] for r in rows) / n, 2) for k in ("turnaround", "waiting", "response")}
    return rows, avg

def simulate(procs, algo, quantum=2):
    validate_processes(procs)
    algo = algo.upper()
    if algo not in ALGOS:
        raise ValueError(f"unknown algorithm {algo}")
    _int(quantum, "quantum", 1)
    rem = {p["pid"]: p["burst"] for p in procs}
    finish, first, ticks = {}, {}, []
    if algo == "RR":
        order = sorted(procs, key=lambda p: (p["arrival"], str(p["pid"])))
        q, i, t = deque(), 0, 0
        def admit():
            nonlocal i
            while i < len(order) and order[i]["arrival"] <= t:
                q.append(order[i]["pid"]); i += 1
        while len(finish) < len(procs):
            admit()
            if not q:
                ticks.append("IDLE"); t += 1; continue
            pid = q.popleft()
            first.setdefault(pid, t)
            run = min(quantum, rem[pid])
            ticks += [pid] * run; t += run; rem[pid] -= run
            admit()
            if rem[pid]: q.append(pid)
            else: finish[pid] = t
    else:
        keys = {"FCFS": lambda p: (p["arrival"], str(p["pid"])),
                "SJF": lambda p: (p["burst"], p["arrival"]),
                "SRTF": lambda p: (rem[p["pid"]], p["arrival"]),
                "PRIORITY": lambda p: (p.get("priority", 0), p["arrival"])}
        preempt = algo == "SRTF"
        t, cur = 0, None
        while len(finish) < len(procs):
            ready = [p for p in procs if p["arrival"] <= t and rem[p["pid"]] > 0]
            if not ready:
                ticks.append("IDLE"); t += 1; cur = None; continue
            if cur is None or preempt:
                cur = min(ready, key=keys[algo])["pid"]
            first.setdefault(cur, t)
            ticks.append(cur); rem[cur] -= 1; t += 1
            if rem[cur] == 0:
                finish[cur] = t; cur = None
    rows, avg = _metrics(procs, finish, first)
    gantt = _compress(ticks)
    busy = sum(1 for x in ticks if x != "IDLE")
    res = {"algo": algo, "gantt": gantt, "table": rows, "avg": avg,
           "cpu_util": round(100 * busy / len(ticks), 1),
           "throughput": round(len(procs) / len(ticks), 3),
           "context_switches": max(0, len([g for g in gantt if g[0] != "IDLE"]) - 1)}
    log.info("scheduler %s avg=%s", algo, avg)
    return res

def compare(procs, quantum=2):
    return [simulate(procs, a, quantum) for a in ALGOS]
