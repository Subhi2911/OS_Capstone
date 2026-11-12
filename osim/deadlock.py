"""Deadlock avoidance/detection: Banker's algorithm."""
from .common import InputError, log

def _check(alloc, maxm, avail):
    n = len(alloc)
    if not n or len(maxm) != n:
        raise InputError("allocation and max must be non-empty and same length")
    m = len(avail)
    for row in alloc + maxm + [avail]:
        if len(row) != m or any((not isinstance(x, int)) or x < 0 for x in row):
            raise InputError("matrices must be rectangular non-negative integers")
    for i in range(n):
        if any(a > b for a, b in zip(alloc[i], maxm[i])):
            raise InputError(f"P{i}: allocation exceeds declared maximum")

def safety(alloc, maxm, avail):
    _check(alloc, maxm, avail)
    n, m = len(alloc), len(avail)
    need = [[maxm[i][j] - alloc[i][j] for j in range(m)] for i in range(n)]
    work, done, seq = list(avail), [False] * n, []
    progress = True
    while progress:
        progress = False
        for i in range(n):
            if not done[i] and all(need[i][j] <= work[j] for j in range(m)):
                work = [work[j] + alloc[i][j] for j in range(m)]
                done[i] = True; seq.append(i); progress = True
    log.info("banker safe=%s seq=%s", all(done), seq)
    return {"safe": all(done), "sequence": seq, "need": need,
            "deadlocked": [i for i in range(n) if not done[i]]}

def request(alloc, maxm, avail, pid, req):
    _check(alloc, maxm, avail)
    if not isinstance(pid, int) or not 0 <= pid < len(alloc):
        raise InputError("invalid process id")
    if len(req) != len(avail) or any(x < 0 for x in req):
        raise InputError("invalid request vector")
    need = [maxm[pid][j] - alloc[pid][j] for j in range(len(avail))]
    if any(r > n for r, n in zip(req, need)):
        return {"granted": False, "reason": "request exceeds declared maximum need"}
    if any(r > a for r, a in zip(req, avail)):
        return {"granted": False, "reason": "resources not available; process must wait"}
    a2 = [list(r) for r in alloc]; a2[pid] = [x + y for x, y in zip(a2[pid], req)]
    v2 = [a - r for a, r in zip(avail, req)]
    s = safety(a2, maxm, v2)
    return {"granted": s["safe"], "sequence": s["sequence"],
            "reason": "safe state preserved" if s["safe"] else "would lead to unsafe state"}
