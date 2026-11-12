#!/usr/bin/env bash
# Bash front-end for the OS simulator (Linux, macOS, WSL, Git Bash on Windows).
# Usage: bash run.sh [menu|demo|test|sysinfo|clean]
cd "$(dirname "$0")" || exit 1

# Pick a working Python (Windows often has python/py, not python3)
PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys" >/dev/null 2>&1; then PY="$c"; break; fi
done
pause() { if [ -t 0 ] && [ -z "${NO_PAUSE:-}" ]; then read -r -p "Press Enter to close..." _; fi; return 0; }
if [ -z "$PY" ]; then echo "ERROR: Python not found. Install Python 3 and tick 'Add to PATH'."; pause; exit 1; fi
"$PY" -c "import matplotlib" 2>/dev/null || { echo "Installing matplotlib..."; "$PY" -m pip install matplotlib || { echo "pip failed"; pause; exit 1; }; }
mkdir -p logs outputs
export PYTHONIOENCODING=utf-8

case "${1:-menu}" in
  menu)    "$PY" -m osim ;;
  demo)    "$PY" -m osim --all | tee outputs/sample_output_trace.txt
           echo "--- last log lines ---"; tail -n 5 logs/activity.log
           echo "Charts saved in: $(pwd)/outputs" ;;
  test)    "$PY" -m unittest discover -s tests -v 2>&1 | tee outputs/test_results.txt ;;
  sysinfo) bash scripts/sysinfo.sh ;;
  clean)   rm -f outputs/* logs/*.log ;;
  *) echo "Usage: bash run.sh [menu|demo|test|sysinfo|clean]" ;;
esac
pause
