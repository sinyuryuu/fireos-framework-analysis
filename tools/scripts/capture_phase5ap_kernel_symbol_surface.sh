#!/usr/bin/env bash
set -u

usage() {
  cat <<'EOF'
Usage: capture_phase5ap_kernel_symbol_surface.sh --serial SERIAL --test-id ID --output DIR [--dry-run]

Read-only kernel symbol visibility capture. It reads procfs metadata and symbol
names only; it does not read a raw device, invoke an ioctl, trigger a race, or
write any device state.
EOF
}

serial=""
test_id=""
output=""
dry_run=0

while (($#)); do
  case "$1" in
    --serial) serial="${2-}"; shift 2 ;;
    --test-id) test_id="${2-}"; shift 2 ;;
    --output) output="${2-}"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$serial" || -z "$test_id" || -z "$output" ]]; then
  usage >&2
  exit 2
fi
if [[ "$output" == "/" || "$output" == "." || "$output" == ".." ]]; then
  echo "refusing broad output path: $output" >&2
  exit 2
fi
if ((dry_run)); then
  printf '%s\n' "DRY-RUN: adb -s $serial read-only kernel symbol surface capture" \
    "test_id=$test_id" "output=$output" "No device command will run."
  exit 0
fi
if [[ -e "$output" ]]; then
  echo "refusing to overwrite existing output: $output" >&2
  exit 3
fi
mkdir -p "$output"
printf 'test_id=%s\nserial=%s\n' "$test_id" "$serial" > "$output/metadata.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$output/timestamp.txt"

run_capture() {
  local name="$1"
  shift
  printf '%q ' "$@" > "$output/$name.command.txt"
  printf '\n' >> "$output/$name.command.txt"
  "$@" > "$output/$name.stdout.txt" 2> "$output/$name.stderr.txt"
  printf '%s\n' "$?" > "$output/$name.exit_code.txt"
}

run_capture adb_state adb -s "$serial" get-state
run_capture identity adb -s "$serial" shell 'getprop ro.build.fingerprint; getprop ro.product.model; getprop ro.product.device; uname -a; id'
run_capture symbol_policy adb -s "$serial" shell 'for p in /proc/kallsyms /proc/sys/kernel/kptr_restrict /proc/sys/kernel/perf_event_paranoid /proc/sys/kernel/yama/ptrace_scope; do echo "### $p"; ls -l "$p" 2>&1; cat "$p" 2>&1; done'
run_capture kallsyms adb -s "$serial" shell 'cat /proc/kallsyms'
run_capture relevant_symbols adb -s "$serial" shell 'grep -E "(remove_waiter|rt_mutex|futex|pi_blocked)" /proc/kallsyms 2>&1 || true'
run_capture modules adb -s "$serial" shell 'cat /proc/modules'
run_capture proc_version adb -s "$serial" shell 'cat /proc/version; cat /proc/cmdline 2>&1; cat /proc/config.gz 2>&1 | gzip -dc 2>&1 | grep -E "^(CONFIG_(FUTEX|RT_MUTEXES|PREEMPT|KALLSYMS|KALLSYMS_ALL|RANDOMIZE_BASE|ARM64|THREAD_INFO_IN_TASK))=" || true'

find "$output" -type f ! -name sha256sums.txt -exec sha256sum {} + | sort > "$output/sha256sums.txt"
printf '%s\n' "Completed read-only capture: $output"
