"""Tables (text/markdown/JSON) and labelled charts."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .common import OUT_DIR, log

def table(headers, rows):
    w = [max(len(str(x)) for x in col) for col in zip(headers, *rows)]
    line = "+" + "+".join("-" * (x + 2) for x in w) + "+"
    fmt = lambda r: "| " + " | ".join(str(c).ljust(x) for c, x in zip(r, w)) + " |"
    return "\n".join([line, fmt(headers), line] + [fmt(r) for r in rows] + [line])

def _save(fig, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, name)
    fig.tight_layout(); fig.savefig(p, dpi=110); plt.close(fig)
    log.info("chart saved %s", name)
    return p

def gantt_chart(results):
    fig, axes = plt.subplots(len(results), 1, figsize=(9, 1.3 * len(results) + 1), sharex=True)
    pids = sorted({g[0] for r in results for g in r["gantt"] if g[0] != "IDLE"})
    col = {p: plt.cm.tab10(i) for i, p in enumerate(pids)}
    for ax, r in zip(axes, results):
        for pid, s, e in r["gantt"]:
            ax.barh(0, e - s, left=s, color="#ccc" if pid == "IDLE" else col[pid], edgecolor="k")
            ax.text((s + e) / 2, 0, pid if pid != "IDLE" else "", ha="center", va="center", fontsize=7)
        ax.set_yticks([]); ax.set_ylabel(r["algo"], rotation=0, ha="right", va="center")
    axes[-1].set_xlabel("Time (units)")
    axes[0].set_title("CPU Scheduling Gantt Charts")
    return _save(fig, "gantt.png")

def sched_chart(results):
    import numpy as np
    x = np.arange(len(results)); w = 0.27
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, k in enumerate(("waiting", "turnaround", "response")):
        ax.bar(x + (i - 1) * w, [r["avg"][k] for r in results], w, label=f"Avg {k}")
    ax.set_xticks(x); ax.set_xticklabels([r["algo"] for r in results])
    ax.set_ylabel("Time units"); ax.set_xlabel("Algorithm")
    ax.set_title("Scheduling comparison (lower is better)"); ax.legend()
    return _save(fig, "scheduling_comparison.png")

def line_chart(series, title, xlabel, ylabel, name):
    fig, ax = plt.subplots(figsize=(7, 4))
    for label, (xs, ys) in series.items():
        ax.plot(xs, ys, marker="o", label=label)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.grid(alpha=.3); ax.legend()
    return _save(fig, name)

def bar_chart(labels, values, title, ylabel, name):
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color="#4c72b0")
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v, str(v), ha="center", va="bottom")
    ax.set_title(title); ax.set_ylabel(ylabel); ax.set_xlabel("Algorithm")
    return _save(fig, name)

def save_json(obj, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w") as f:
        json.dump(obj, f, indent=2, default=str)
