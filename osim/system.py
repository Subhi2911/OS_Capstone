"""Python<->Bash bridge."""
import shutil
import os, subprocess
from .common import ROOT, log

def host_snapshot(timeout=10):
    script = os.path.join(ROOT, "scripts", "sysinfo.sh")
    try:
        bash_cmd = shutil.which("bash") or "bash"
        out = subprocess.run([bash_cmd, script], capture_output=True, text=True,
                             timeout=timeout, check=True).stdout
    except (subprocess.SubprocessError, OSError) as e:
        log.error("sysinfo failed: %s", e)
        return {"error": str(e)}
    log.info("host snapshot ok")
    return dict(l.strip().split("=", 1) for l in out.splitlines() if "=" in l)
