#!/usr/bin/env bash
set -u

usage() {
  cat <<'EOF'
Usage: capture_phase5an_boot_metadata.sh --serial SERIAL --test-id ID --output DIR [--attempt-boot-pull] [--dry-run]

Read-only exact-device metadata capture. It never writes a device partition,
remounts anything, invokes fastboot, or executes a payload. --attempt-boot-pull
only records whether the shell can read /dev/block/by-name/boot; a denied pull
is an expected, preserved result.
EOF
}

serial=""
test_id=""
output=""
attempt_boot_pull=0
dry_run=0

while (($#)); do
  case "$1" in
    --serial) serial="${2-}"; shift 2 ;;
    --test-id) test_id="${2-}"; shift 2 ;;
    --output) output="${2-}"; shift 2 ;;
    --attempt-boot-pull) attempt_boot_pull=1; shift ;;
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
  printf '%s\n' "DRY-RUN: adb -s $serial read-only metadata capture" \
    "test_id=$test_id" "output=$output" \
    "attempt_boot_pull=$attempt_boot_pull" \
    "No device command will run."
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

run_capture adb_devices adb devices -l
run_capture adb_state adb -s "$serial" get-state
run_capture identity adb -s "$serial" shell 'getprop ro.build.fingerprint; getprop ro.product.model; getprop ro.product.device; getprop ro.hardware; uname -a; id'
run_capture boot_links adb -s "$serial" shell 'ls -l /dev/block/by-name; ls -l /dev/block/platform/*/by-name'
run_capture proc_visibility adb -s "$serial" shell 'for p in /proc/bootconfig /proc/cmdline /proc/version /proc/config.gz /sys/firmware/fdt /sys/firmware/devicetree/base/model; do echo "### $p"; ls -l "$p"; done'
run_capture config_gates adb -s "$serial" shell 'zcat /proc/config.gz 2>/dev/null | grep -E "^(CONFIG_(ARM64|ARM64_4K_PAGES|ARM64_VA_BITS_39|FUTEX|RT_MUTEXES|PREEMPT|RANDOMIZE_BASE|THREAD_INFO_IN_TASK|DEBUG_RT_MUTEXES|SECURITY_SELINUX|SECCOMP))=" || true'

if ((attempt_boot_pull)); then
  printf '%s\n' "adb -s $serial pull /dev/block/by-name/boot $output/boot.raw" > "$output/boot_pull.command.txt"
  adb -s "$serial" pull /dev/block/by-name/boot "$output/boot.raw" > "$output/boot_pull.stdout.txt" 2> "$output/boot_pull.stderr.txt"
  printf '%s\n' "$?" > "$output/boot_pull.exit_code.txt"
fi

find "$output" -type f ! -name sha256sums.txt -exec sha256sum {} + | sort > "$output/sha256sums.txt"
printf '%s\n' "Completed read-only capture: $output"
