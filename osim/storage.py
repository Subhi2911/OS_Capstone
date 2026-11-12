"""Disk scheduling: FCFS, SSTF, SCAN, C-SCAN, LOOK."""
from .common import validate_positive_list, _int, log

DISK_ALGOS = ["FCFS", "SSTF", "SCAN", "CSCAN", "LOOK"]

def schedule(requests, head, size, algo, direction="up"):
    validate_positive_list(requests, "requests")
    _int(size, "disk size", 1); _int(head, "head", 0)
    if head >= size or any(r >= size for r in requests):
        raise ValueError("track number outside disk range")
    if direction not in ("up", "down"):
        raise ValueError("direction must be 'up' or 'down'")
    algo = algo.upper()
    lo = sorted(r for r in requests if r < head)[::-1]
    hi = sorted(r for r in requests if r >= head)
    if algo == "FCFS":
        order = list(requests)
    elif algo == "SSTF":
        pend, cur, order = list(requests), head, []
        while pend:
            n = min(pend, key=lambda r: abs(r - cur)); pend.remove(n); order.append(n); cur = n
    elif algo in ("SCAN", "LOOK"):
        first, second = (hi, lo) if direction == "up" else (lo, hi)
        order = list(first)
        if algo == "SCAN":
            order.append(size - 1 if direction == "up" else 0)
        order += second
    elif algo == "CSCAN":
        if direction == "up":
            order = hi + ([size - 1, 0] if lo else []) + lo[::-1]
        else:
            order = lo + ([0, size - 1] if hi else []) + hi[::-1]
    else:
        raise ValueError(f"unknown disk algorithm {algo}")
    cur, total = head, 0
    for t in order:
        total += abs(t - cur); cur = t
    res = {"algo": algo, "order": order, "total_movement": total,
           "avg_seek": round(total / len(requests), 2)}
    log.info("disk %s total=%d", algo, total)
    return res
