"""Shared helpers: logging, validation, input loading."""
import json, logging, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT, "logs")
OUT_DIR = os.path.join(ROOT, "outputs")

class InputError(ValueError):
    """Raised for invalid user/input-file data."""

def get_logger():
    os.makedirs(LOG_DIR, exist_ok=True)
    lg = logging.getLogger("osim")
    if not lg.handlers:
        lg.setLevel(logging.INFO)
        h = logging.FileHandler(os.path.join(LOG_DIR, "activity.log"))
        h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        lg.addHandler(h)
    return lg
log = get_logger()

def _int(v, name, lo=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise InputError(f"{name} must be an integer, got {v!r}")
    if lo is not None and v < lo:
        raise InputError(f"{name} must be >= {lo}, got {v}")
    return v

def validate_processes(procs):
    if not isinstance(procs, list) or not procs:
        raise InputError("process list must be a non-empty list")
    seen = set()
    for p in procs:
        if not isinstance(p, dict) or "pid" not in p:
            raise InputError("each process needs a 'pid'")
        if p["pid"] in seen:
            raise InputError(f"duplicate pid {p['pid']}")
        seen.add(p["pid"])
        _int(p.get("arrival"), f"{p['pid']}.arrival", 0)
        _int(p.get("burst"), f"{p['pid']}.burst", 1)
        _int(p.get("priority", 0), f"{p['pid']}.priority", 0)

def validate_positive_list(xs, name):
    if not isinstance(xs, list) or not xs:
        raise InputError(f"{name} must be a non-empty list")
    for x in xs:
        _int(x, name, 0)

def load_input(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError:
        raise InputError(f"input file not found: {path}")
    except json.JSONDecodeError as e:
        raise InputError(f"malformed JSON in {path}: {e}")
    log.info("loaded input %s", path)
    return data
