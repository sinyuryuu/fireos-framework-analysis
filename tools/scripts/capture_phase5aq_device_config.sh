#!/usr/bin/env bash
set -u

usage() {
  cat <<'EOF'
Usage: capture_phase5aq_device_config.sh --serial SERIAL --test-id ID --output DIR [--dry-run]

Read-only capture of /proc/config.gz and device identity. It does not change
device state or access any block device.
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
if [[ -z "$serial" || -z "$test_id" || -z "$output" ]]; then usage >&2; exit 2; fi
if [[ "$output" == "/" || "$output" == "." || "$output" == ".." ]]; then echo "refusing broad output path" >&2; exit 2; fi
if ((dry_run)); then
  printf '%s\n' "DRY-RUN: adb -s $serial read-only config capture" "test_id=$test_id" "output=$output" "No device command will run."
  exit 0
fi
if [[ -e "$output" ]]; then echo "refusing to overwrite existing output: $output" >&2; exit 3; fi
mkdir -p "$output"
printf 'test_id=%s\nserial=%s\n' "$test_id" "$serial" > "$output/metadata.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$output/timestamp.txt"

printf '%s\n' "adb -s $serial get-state" > "$output/adb_state.command.txt"
adb -s "$serial" get-state > "$output/adb_state.stdout.txt" 2> "$output/adb_state.stderr.txt"
printf '%s\n' "$?" > "$output/adb_state.exit_code.txt"

printf '%s\n' "adb -s $serial shell getprop ro.build.fingerprint; uname -a; id" > "$output/identity.command.txt"
adb -s "$serial" shell 'getprop ro.build.fingerprint; getprop ro.product.model; getprop ro.product.device; uname -a; id' > "$output/identity.stdout.txt" 2> "$output/identity.stderr.txt"
printf '%s\n' "$?" > "$output/identity.exit_code.txt"

printf '%s\n' "adb -s $serial exec-out cat /proc/config.gz" > "$output/config.command.txt"
adb -s "$serial" exec-out cat /proc/config.gz > "$output/config.gz" 2> "$output/config.stderr.txt"
printf '%s\n' "$?" > "$output/config.exit_code.txt"

if gzip -t "$output/config.gz" 2> "$output/config-gzip.stderr.txt"; then
  gzip -dc "$output/config.gz" > "$output/kernel.config"
  printf '%s\n' 0 > "$output/config-gzip.exit_code.txt"
else
  printf '%s\n' 1 > "$output/config-gzip.exit_code.txt"
fi

find "$output" -type f ! -name sha256sums.txt -exec sha256sum {} + | sort > "$output/sha256sums.txt"
printf '%s\n' "Completed read-only capture: $output"
