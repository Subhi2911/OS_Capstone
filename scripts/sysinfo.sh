#!/usr/bin/env bash
# Live host snapshot (key=value). Falls back gracefully where /proc is missing (e.g. Git Bash).
echo "hostname=$(hostname 2>/dev/null || echo n/a)"
echo "kernel=$(uname -sr 2>/dev/null || echo n/a)"
echo "cpus=$(nproc 2>/dev/null || echo "${NUMBER_OF_PROCESSORS:-1}")"
if [ -r /proc/meminfo ]; then
  echo "mem_total_kb=$(awk '/MemTotal/{print $2}' /proc/meminfo)"
  echo "mem_avail_kb=$(awk '/MemAvailable/{print $2}' /proc/meminfo)"
else
  echo "mem_total_kb=n/a (no /proc on this shell)"
fi
echo "load=$(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null || echo n/a)"
echo "procs=$( (ps -e 2>/dev/null | tail -n +2 | wc -l) || echo n/a)"
echo "disk_root_use=$(df -P / 2>/dev/null | awk 'NR==2{print $5}')"
