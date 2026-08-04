#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: capture_phase5cy_runtime_boundary.sh --serial SERIAL --output DIR [--dry-run]

Read-only PS7331 runtime-boundary capture. It does not enable tracing, change
settings, start or stop processes, call futex, read kernel memory, or reboot.
EOF
}

SERIAL=""
OUTPUT=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --serial) SERIAL="${2:-}"; shift 2 ;;
    --output) OUTPUT="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$SERIAL" || -z "$OUTPUT" ]]; then
  usage >&2
  exit 2
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  printf '%s\n' \
    "DRY-RUN: no device or filesystem changes" \
    "adb -s $SERIAL devices -l" \
    "adb -s $SERIAL shell getprop" \
    "adb -s $SERIAL shell ps -A -o USER,PID,PPID,NAME,ARGS" \
    "adb -s $SERIAL shell cat /proc/<pid>/status" \
    "adb -s $SERIAL shell ls -ld /sys/kernel/debug/tracing /sys/kernel/tracing /proc/kallsyms /proc/kcore /dev/kmem" \
    "adb -s $SERIAL shell cat /proc/sys/kernel/perf_event_paranoid" \
    "adb -s $SERIAL logcat -b all -d -v threadtime"
  exit 0
fi

if [[ -e "$OUTPUT" ]]; then
  echo "Refusing to overwrite existing output: $OUTPUT" >&2
  exit 2
fi

command -v adb >/dev/null || { echo "adb not found" >&2; exit 2; }
mkdir -p "$OUTPUT"

adb_cmd() {
  adb -s "$SERIAL" "$@"
}

if ! adb_cmd get-state 2>/dev/null | grep -qx device; then
  echo "Serial is not connected in device state: $SERIAL" >&2
  exit 3
fi

date -u +%Y-%m-%dT%H:%M:%SZ > "$OUTPUT/timestamp_utc.txt"
{
  echo "adb -s $SERIAL devices -l"
  echo "adb -s $SERIAL shell getprop"
  echo "adb -s $SERIAL shell id"
  echo "adb -s $SERIAL shell getenforce"
  echo "adb -s $SERIAL shell cat /proc/version"
  echo "adb -s $SERIAL shell ps -A -o USER,PID,PPID,NAME,ARGS"
  echo "adb -s $SERIAL shell cat /proc/<pid>/status for selected processes"
  echo "adb -s $SERIAL shell tracing and kernel-observation visibility checks"
  echo "adb -s $SERIAL logcat -b all -d -v threadtime | futex/rtmutex/requeue/seccomp filter"
} > "$OUTPUT/commands.txt"

adb_cmd devices -l > "$OUTPUT/adb-devices.txt"
adb_cmd shell getprop > "$OUTPUT/getprop.txt"
{
  echo '=== id'
  adb_cmd shell id
  echo '=== getenforce'
  adb_cmd shell getenforce
  echo '=== proc_version'
  adb_cmd shell cat /proc/version
} > "$OUTPUT/device-security.txt" 2>&1

adb_cmd shell ps -A -o USER,PID,PPID,NAME,ARGS > "$OUTPUT/process-list.txt" 2>&1

{
  for name in system_server adbd com.android.systemui com.amazon.firelauncher \
      com.microsoft.launcher com.amazon.device.software.ota; do
    echo "=== $name"
    pids="$(adb_cmd shell pidof "$name" 2>/dev/null | tr -d '\r')" || true
    if [[ -z "$pids" ]]; then
      echo "PID_NOT_FOUND"
      continue
    fi
    for pid in $pids; do
      echo "--- /proc/$pid/status"
      adb_cmd shell cat "/proc/$pid/status" 2>&1 || true
    done
  done
} > "$OUTPUT/process-status.txt"

adb_cmd shell 'for p in /sys/kernel/debug/tracing /sys/kernel/tracing /sys/kernel/debug/tracing/events/futex /sys/kernel/tracing/events/futex /proc/kallsyms /proc/kcore /dev/kmem; do echo ===$p; ls -ld "$p" 2>&1; done; echo ===perf_event_paranoid; cat /proc/sys/kernel/perf_event_paranoid 2>&1; echo ===futex_event_dirs; find /sys/kernel/debug/tracing/events -maxdepth 2 -type d -iname "*futex*" 2>&1 | head -40' > "$OUTPUT/tracing-visibility.txt" 2>&1

adb_cmd logcat -b all -d -v threadtime | rg -i 'futex|rtmutex|requeue|seccomp|sig(sys|segv|abrt)' > "$OUTPUT/logcat-futex-boundary.txt" || true

{
  echo "PS7331 runtime-boundary capture"
  echo "serial=$SERIAL"
  echo "scope=read-only; no futex trigger, tracing enable, process control, kernel memory or reboot"
  echo "identity_mismatch_observed=false"
  echo "cleanup_residue_observed=false"
} > "$OUTPUT/result.md"

(cd "$OUTPUT" && shasum -a 256 * > sha256sums.txt)
echo "Wrote read-only runtime-boundary capture to $OUTPUT"
