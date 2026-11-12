"""Memory: page replacement (FIFO/LRU/OPT) and contiguous allocation (First/Best/Worst fit)."""
from .common import validate_positive_list, _int, log

PAGE_ALGOS = ["FIFO", "LRU", "OPT"]
FIT_ALGOS = ["FIRST", "BEST", "WORST"]

def page_replace(refs, frames, algo):
    validate_positive_list(refs, "reference string")
    _int(frames, "frames", 1)
    algo = algo.upper()
    if algo not in PAGE_ALGOS:
        raise ValueError(f"unknown page algorithm {algo}")
    mem, faults, trace = [], 0, []
    for i, p in enumerate(refs):
        hit = p in mem
        if not hit:
            faults += 1
            if len(mem) >= frames:
                if algo == "FIFO":
                    mem.pop(0)
                elif algo == "LRU":
                    last = {x: max(j for j in range(i) if refs[j] == x) for x in mem}
                    mem.remove(min(mem, key=last.get))
                else:
                    def nxt(x):
                        for j in range(i + 1, len(refs)):
                            if refs[j] == x: return j
                        return float("inf")
                    mem.remove(max(mem, key=nxt))
            mem.append(p)
        trace.append((p, list(mem), "HIT" if hit else "FAULT"))
    res = {"algo": algo, "frames": frames, "faults": faults,
           "hit_ratio": round(100 * (len(refs) - faults) / len(refs), 1), "trace": trace}
    log.info("page %s frames=%d faults=%d", algo, frames, faults)
    return res

def allocate(partitions, requests, algo):
    validate_positive_list(partitions, "partitions")
    validate_positive_list(requests, "requests")
    algo = algo.upper()
    if algo not in FIT_ALGOS:
        raise ValueError(f"unknown fit algorithm {algo}")
    free, placed = list(partitions), []
    for r in requests:
        cands = [i for i, f in enumerate(free) if f >= r]
        if not cands:
            placed.append((r, None)); continue
        i = (cands[0] if algo == "FIRST" else
             min(cands, key=lambda k: free[k]) if algo == "BEST" else
             max(cands, key=lambda k: free[k]))
        placed.append((r, i)); free[i] -= r
    used = sum(r for r, i in placed if i is not None)
    res = {"algo": algo, "placed": placed, "free_after": free,
           "unallocated": [r for r, i in placed if i is None],
           "ext_fragmentation": sum(free),
           "utilisation": round(100 * used / sum(partitions), 1)}
    log.info("alloc %s unallocated=%s", algo, res["unallocated"])
    return res
