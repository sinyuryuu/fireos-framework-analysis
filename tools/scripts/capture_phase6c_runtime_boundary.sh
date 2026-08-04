#!/usr/bin/env bash
# Phase 6C: bounded, read-only runtime-boundary capture.
#
# This script never invokes futex, opens a device node, changes settings or
# package state, starts/stops an app, enables tracing, reboots, or reads kernel
# memory.  The output directory is host-side and must be new.
set -u
export LC_ALL=C

SERIAL=""
OUTPUT=""
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

usage() {
  cat <<'EOF'
Usage: capture_phase6c_runtime_boundary.sh --serial SERIAL --output DIR [--dry-run]

Captures only read-only ADB/proc/package metadata for the selected device.
The command refuses to overwrite an existing output directory.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in
  /|.|..|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;;
esac

COMMAND_NAMES=(
  serial state props identity selinux kernel_version kernel_uname
  proc_kallsyms_metadata proc_kallsyms_head proc_slabinfo_metadata
  proc_slabinfo_head kaslr_setting home_resolution home_candidates
  firelauncher_path firelauncher_package launcher_packages setup_state
  setup_state_global preferred_activities activity_activities window_windows
)

if [ "$DRY_RUN" -eq 1 ]; then
  printf '%s\n' \
    'DRY-RUN: no device command will run and no files will be written.' \
    "serial=$SERIAL" "output=$OUTPUT" \
    "commands=${COMMAND_NAMES[*]}"
  exit 0
fi

command -v adb >/dev/null 2>&1 || die 'adb is required'
command -v shasum >/dev/null 2>&1 || die 'shasum is required'
[ ! -e "$OUTPUT" ] || die "refusing to overwrite existing output: $OUTPUT"

ADB=(adb -s "$SERIAL")
if ! [ "$(${ADB[@]} get-state 2>/dev/null | tr -d '\r')" = "device" ]; then
  die "selected serial is not connected in device state: $SERIAL"
fi

mkdir -p "$OUTPUT"
START_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
{
  printf 'schema\tphase6c-runtime-boundary-v1\n'
  printf 'serial\t%s\n' "$SERIAL"
  printf 'start_utc\t%s\n' "$START_UTC"
  printf 'mode\tread-only\n'
} > "$OUTPUT/metadata.tsv"

run_capture() {
  local name="$1"
  shift
  printf '%q ' "$@" > "$OUTPUT/${name}.command.txt"
  printf '\n' >> "$OUTPUT/${name}.command.txt"
  "$@" > "$OUTPUT/${name}.stdout.txt" 2> "$OUTPUT/${name}.stderr.txt"
  local status=$?
  printf '%s\n' "$status" > "$OUTPUT/${name}.exit_code.txt"
  printf '%s\t%s\t%s\n' "$name" "$status" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$OUTPUT/metadata.tsv"
  return 0
}

run_capture serial "${ADB[@]}" get-serialno
run_capture state "${ADB[@]}" get-state
run_capture props "${ADB[@]}" shell getprop
run_capture identity "${ADB[@]}" shell id
run_capture selinux "${ADB[@]}" shell getenforce
run_capture kernel_version "${ADB[@]}" shell cat /proc/version
run_capture kernel_uname "${ADB[@]}" shell uname -a
run_capture proc_kallsyms_metadata "${ADB[@]}" shell ls -lZ /proc/kallsyms
run_capture proc_kallsyms_head "${ADB[@]}" shell head -n 5 /proc/kallsyms
run_capture proc_slabinfo_metadata "${ADB[@]}" shell ls -lZ /proc/slabinfo
run_capture proc_slabinfo_head "${ADB[@]}" shell head -n 20 /proc/slabinfo
run_capture kaslr_setting "${ADB[@]}" shell cat /proc/sys/kernel/randomize_va_space
run_capture home_resolution "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
run_capture home_candidates "${ADB[@]}" shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME
run_capture firelauncher_path "${ADB[@]}" shell pm path com.amazon.firelauncher
run_capture firelauncher_package "${ADB[@]}" shell dumpsys package com.amazon.firelauncher
run_capture launcher_packages "${ADB[@]}" shell 'pm list packages | grep -iE "amazon|launcher|home|systemui|futex|rtmutex"'
run_capture setup_state "${ADB[@]}" shell settings get secure user_setup_complete
run_capture setup_state_global "${ADB[@]}" shell settings get global device_provisioned
run_capture preferred_activities "${ADB[@]}" shell dumpsys package preferred-activities
run_capture activity_activities "${ADB[@]}" shell dumpsys activity activities
run_capture window_windows "${ADB[@]}" shell dumpsys window windows

END_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'end_utc\t%s\n' "$END_UTC" >> "$OUTPUT/metadata.tsv"
cat > "$OUTPUT/result.md" <<EOF
# Phase 6C runtime boundary capture

- Serial: $SERIAL
- Start UTC: $START_UTC
- End UTC: $END_UTC
- Device writes: none
- Device nodes opened: none
- Block devices read: none
- Futex or requeue operation: none
- Tracing enabled: no
- Process/package/settings state changed: no
- Kernel memory read/write: no

Individual command stdout, stderr and exit status files are retained. A
permission-denied result is evidence about the shell boundary; it is not a
kernel-state inference.
EOF

(cd "$OUTPUT" && find . -type f ! -name sha256sums.txt -print0 | sort -z | while IFS= read -r -d '' file; do
  shasum -a 256 "$file"
done) > "$OUTPUT/sha256sums.txt"
printf 'Captured read-only Phase 6C runtime boundary in %s\n' "$OUTPUT"
