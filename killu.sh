#!/bin/bash
# kill_ubuntu_all.sh
# Grabs all processes in the PRoot container and kills them safely.

ME=$$
PP=$PPID

echo "[*] Current shell PID: $ME  Parent PID: $PP"
echo

# Grab ALL PIDs visible in this PRoot environment
PIDS=$(ps -A -o pid=)

if [ -z "$PIDS" ]; then
  echo "[*] No processes found."
  exit 0
fi

TARGETS=""

echo "Found the following background processes (PID : CMD):"
for pid in $PIDS; do
  # Clean up whitespace
  pid=$(echo "$pid" | tr -d ' ')
  
  # Exclude PID 1 (usually the proot login shell/init), this script, and its parent
  if [ "$pid" -eq 1 ] 2>/dev/null || [ "$pid" -eq "$ME" ] 2>/dev/null || [ "$pid" -eq "$PP" ] 2>/dev/null; then
    continue
  fi
  
  # Fetch the command string
  cmd=$(ps -p "$pid" -o cmd= 2>/dev/null)
  
  # Only list it if the process is still actively returning a command
  if [ -n "$cmd" ]; then
      echo "  $pid : $cmd"
      TARGETS="$TARGETS $pid"
  fi
done

if [ -z "$TARGETS" ]; then
  echo "[*] Only system/shell processes are running. Nothing to kill."
  exit 0
fi

echo
read -p "Kill all listed processes? (y/N) " ans
case "$ans" in
  y|Y)
    for pid in $TARGETS; do
      kill -9 "$pid" 2>/dev/null && echo "killed $pid" || echo "failed to kill $pid"
    done
    echo "[*] Done."
    ;;
  *)
    echo "[*] Aborted. No processes were killed."
    ;;
esac
