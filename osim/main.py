"""Integrated menu-driven application and batch runner."""
import argparse, os, sys
from . import scheduler, memory, deadlock, storage, system, report
from .common import ROOT, InputError, load_input, log

DEFAULT_INPUT = os.path.join(ROOT, "data", "sample_input.json")

def run_scheduling(d):
    print("\n=== CPU SCHEDULING ===")
    res = scheduler.compare(d["processes"], d.get("quantum", 2))
    for r in res:
        print(f"\n-- {r['algo']} --  Gantt: " + " ".join(f"[{p} {s}-{e}]" for p, s, e in r["gantt"]))
        print(report.table(["PID", "AT", "BT", "CT", "TAT", "WT", "RT"],
              [[x["pid"], x["arrival"], x["burst"], x["completion"], x["turnaround"], x["waiting"], x["response"]] for x in r["table"]]))
    print("\nSummary")
    print(report.table(["Algo", "AvgWT", "AvgTAT", "AvgRT", "CPU%", "Thrput", "CtxSw"],
          [[r["algo"], r["avg"]["waiting"], r["avg"]["turnaround"], r["avg"]["response"],
            r["cpu_util"], r["throughput"], r["context_switches"]] for r in res]))
    report.gantt_chart(res); report.sched_chart(res)
    return res

def run_memory(d):
    print("\n=== MEMORY: PAGE REPLACEMENT ===")
    refs, fr = d["page_refs"], d["frames"]
    pr = [memory.page_replace(refs, fr, a) for a in memory.PAGE_ALGOS]
    for r in pr:
        print(f"\n-- {r['algo']} ({fr} frames) --")
        print(report.table(["Ref", "Frames", "Result"], [[p, m, s] for p, m, s in r["trace"]]))
    print(report.table(["Algo", "Faults", "Hit %"], [[r["algo"], r["faults"], r["hit_ratio"]] for r in pr]))
    rng = list(range(1, 8))
    series = {a: (rng, [memory.page_replace(refs, f, a)["faults"] for f in rng]) for a in memory.PAGE_ALGOS}
    report.line_chart(series, "Page faults vs frames", "Frames", "Page faults", "page_faults.png")
    bel = d.get("belady_refs")
    belady = None
    if bel:
        fifo = [memory.page_replace(bel, f, "FIFO")["faults"] for f in rng]
        lru = [memory.page_replace(bel, f, "LRU")["faults"] for f in rng]
        report.line_chart({"FIFO": (rng, fifo), "LRU": (rng, lru)},
                          "Belady's anomaly (ref: 1 2 3 4 1 2 5 1 2 3 4 5)", "Frames", "Page faults", "belady.png")
        belady = {"FIFO": fifo, "LRU": lru}
        print("\nBelady test FIFO faults by frames 1..7:", fifo, "| LRU:", lru)
        if fifo[3] > fifo[2]: print("  -> Anomaly: FIFO faults rose from 3 to 4 frames.")
    print("\n=== MEMORY: CONTIGUOUS ALLOCATION ===")
    al = [memory.allocate(d["partitions"], d["requests"], a) for a in memory.FIT_ALGOS]
    print(report.table(["Algo", "Placement(req->part)", "Unallocated", "Free left", "Util %"],
          [[r["algo"], ", ".join(f"{q}->{'P'+str(i) if i is not None else 'X'}" for q, i in r["placed"]),
            r["unallocated"], r["ext_fragmentation"], r["utilisation"]] for r in al]))
    report.bar_chart([r["algo"] for r in al], [r["ext_fragmentation"] for r in al],
                     "Free memory left after allocation", "KB free", "allocation.png")
    return {"paging": pr, "alloc": al, "belady": belady}

def run_deadlock(d):
    print("\n=== DEADLOCK: BANKER'S ALGORITHM ===")
    b = d["banker"]
    s = deadlock.safety(b["allocation"], b["max"], b["available"])
    print("Need matrix:", s["need"])
    print("Safe state:", s["safe"], "| Safe sequence:", " -> ".join(f"P{i}" for i in s["sequence"]) or "none",
          "| Deadlocked:", [f"P{i}" for i in s["deadlocked"]])
    out = {"safety": s}
    if "request" in b:
        q = deadlock.request(b["allocation"], b["max"], b["available"], b["request"]["pid"], b["request"]["vector"])
        print(f"Request P{b['request']['pid']} {b['request']['vector']}: granted={q['granted']} ({q['reason']})")
        out["request"] = q
    return out

def run_storage(d):
    print("\n=== STORAGE: DISK SCHEDULING ===")
    k = d["disk"]
    res = [storage.schedule(k["requests"], k["head"], k["size"], a, k.get("direction", "up")) for a in storage.DISK_ALGOS]
    print(f"Head={k['head']}  Disk size={k['size']}  Requests={k['requests']}")
    print(report.table(["Algo", "Service order", "Total movement", "Avg seek"],
          [[r["algo"], " ".join(map(str, r["order"])), r["total_movement"], r["avg_seek"]] for r in res]))
    report.bar_chart([r["algo"] for r in res], [r["total_movement"] for r in res],
                     "Total head movement (tracks)", "Tracks", "disk_seek.png")
    return res

def run_system():
    print("\n=== LIVE HOST SNAPSHOT (via Bash) ===")
    s = system.host_snapshot()
    for k, v in s.items(): print(f"  {k:15s}: {v}")
    return s

def run_all(d):
    out = {"scheduling": run_scheduling(d), "memory": run_memory(d), "deadlock": run_deadlock(d),
           "storage": run_storage(d), "host": run_system()}
    report.save_json(out, "results.json")
    print("\nCharts and results.json saved in outputs/")
    return out

def _ask(prompt, cast=int):
    try:
        return cast(input(prompt))
    except ValueError:
        raise InputError("invalid entry")

def menu(d):
    items = {"1": ("CPU scheduling comparison", run_scheduling), "2": ("Memory management", run_memory),
             "3": ("Deadlock (Banker's)", run_deadlock), "4": ("Disk scheduling", run_storage),
             "5": ("Live host snapshot (Bash)", lambda _: run_system()), "6": ("Run everything + charts", run_all)}
    while True:
        print("\n===== OS RESOURCE-MANAGEMENT SIMULATOR =====")
        for k, (n, _) in items.items(): print(f" {k}. {n}")
        print(" 7. Custom page-replacement run\n 0. Exit")
        try:
            c = input("Choice: ").strip()
            if c == "0": break
            if c in items:
                log.info("menu choice %s", c); items[c][1](d)
            elif c == "7":
                refs = [int(x) for x in input("Reference string (space separated): ").split()]
                fr = _ask("Frames: ")
                a = input("Algorithm FIFO/LRU/OPT: ")
                r = memory.page_replace(refs, fr, a)
                print(f"{r['algo']}: {r['faults']} faults, hit ratio {r['hit_ratio']}%")
            else:
                print("Invalid choice.")
        except (InputError, ValueError) as e:
            print(f"[input error] {e}"); log.warning("input error: %s", e)
        except (EOFError, KeyboardInterrupt):
            print(); break

def main(argv=None):
    ap = argparse.ArgumentParser(description="OS resource-management simulator")
    ap.add_argument("--input", default=DEFAULT_INPUT)
    ap.add_argument("--all", action="store_true", help="run all modules non-interactively")
    a = ap.parse_args(argv)
    log.info("session start")
    try:
        d = load_input(a.input)
        run_all(d) if a.all else menu(d)
    except InputError as e:
        print(f"[error] {e}", file=sys.stderr); log.error("%s", e); return 2
    except Exception as e:
        print(f"[fatal] {e}", file=sys.stderr); log.exception("unhandled"); return 1
    log.info("session end")
    return 0

if __name__ == "__main__":
    sys.exit(main())
