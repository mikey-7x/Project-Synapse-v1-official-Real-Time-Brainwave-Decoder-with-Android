#!/bin/bash
# kill_ubuntu_safe.sh
# Safely kill background processes without crashing the PRoot session.

ME=$$
PP=$PPID

echo "[*] Current shell PID: $ME  Parent PID: $PP"
echo

# Grab ALL PIDs
PIDS=$(ps -A -o pid=)

if [ -z "$PIDS" ]; then
  echo "[*] No processes found."
  exit 0
fi

TARGETS=""

echo "Found the following background processes:"
for pid in $PIDS; do
  pid=$(echo "$pid" | tr -d ' ')
  
  # Fetch the command string
  cmd=$(ps -p "$pid" -o cmd= 2>/dev/null)
  
  # Skip empty commands
  if [ -z "$cmd" ]; then
    continue
  fi

  # THE SHIELD: Do not kill bash, sh, proot, su, or the script itself
  if [[ "$cmd" == *"proot"* ]] || [[ "$cmd" == *"bash"* ]] || [[ "$cmd" == *"sh"* ]] || [[ "$cmd" == *"su"* ]] || [[ "$pid" -eq 1 ]] || [[ "$pid" -eq "$ME" ]] || [[ "$pid" -eq "$PP" ]]; then
    continue
  fi
  
  echo "  $pid : $cmd"
  TARGETS="$TARGETS $pid"
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
    echo "[*] Aborted."
    ;;
esac
