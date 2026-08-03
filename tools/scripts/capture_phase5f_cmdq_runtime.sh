#!/usr/bin/env bash
# Read-only CMDQ runtime metadata capture for the exact device.
# This script never opens /dev/mtk_cmdq, issues ioctl, changes settings,
# reboots, enters bootloader mode, uploads a loader, or writes a partition.
set -Eeuo pipefail

SERIAL=""
TEST_ID=""
OUTPUT=""
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --test-id) [ "$#" -ge 2 ] || die '--test-id requires a value'; TEST_ID="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: capture_phase5f_cmdq_runtime.sh --serial SERIAL --test-id ID --output DIR [--dry-run]'
      exit 0
      ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$OUTPUT" ] || die '--output is required'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: verify adb -s %q get-state\n' "$SERIAL"
  printf 'DRY-RUN: collect getprop/id/getenforce and read-only /proc, /sys, module, and config metadata\n'
  printf 'DRY-RUN: write raw outputs and SHA-256 manifest under %q\n' "$OUTPUT"
  exit 0
fi

case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"
mkdir -p "$OUTPUT"

ADB=(adb -s "$SERIAL")
STAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'test_id=%s\nserial=%s\ntimestamp_utc=%s\nread_only=true\n' \
  "$TEST_ID" "$SERIAL" "$STAMP" > "$OUTPUT/metadata.tsv"

run_local() {
  local name="$1"; shift
  printf '%q ' "$@" > "$OUTPUT/$name.command.txt"
  printf '\n' >> "$OUTPUT/$name.command.txt"
  set +e
  "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
}

run_remote() {
  local name="$1"; shift
  # Pass one complete command string to adb shell. Using `sh -c` with
  # separately serialized words would make the first word the command and
  # silently turn later words into positional parameters on Android toybox.
  printf 'adb -s %q shell %q\n' "$SERIAL" "$*" > "$OUTPUT/$name.command.txt"
  set +e
  "${ADB[@]}" shell "$*" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
}

run_local adb_state "${ADB[@]}" get-state
run_local adb_devices "${ADB[@]}" devices -l
run_remote device_identity 'getprop; printf "\\n--- id ---\\n"; id; printf "\\n--- getenforce ---\\n"; getenforce; printf "\\n--- uname ---\\n"; uname -a'
run_remote boot_properties 'getprop | grep -E "ro\\.build\\.|ro\\.product\\.|ro\\.hardware|ro\\.boot\\.(hardware|verifiedbootstate|flash\\.locked|vbmeta\\.device_state)|ro\\.debuggable"'
run_remote cmdline 'cat /proc/cmdline'
run_remote modules 'cat /proc/modules'
run_remote proc_devices 'cat /proc/devices'
run_remote proc_misc 'cat /proc/misc'
run_remote interrupts 'cat /proc/interrupts'
run_remote cmdq_nodes 'ls -lZ /dev/mtk_cmdq /proc/mtk_cmdq /proc/mtk_cmdq_debug 2>&1'
run_remote cmdq_sysfs 'for p in /sys/class/misc/mtk_cmdq /sys/class/misc/mtk_cmdq/dev /sys/class/misc/mtk_cmdq/uevent /sys/class/misc/mtk_cmdq/device/uevent /sys/class/misc/mtk_cmdq/device/modalias; do echo "--- $p"; ls -ldZ "$p" 2>&1; [ -f "$p" ] && cat "$p" 2>&1; done'
run_remote module_paths 'for d in /vendor/lib/modules /system/lib/modules /system/vendor/lib/modules; do echo "--- $d"; find "$d" -maxdepth 2 -type f 2>/dev/null | sort; done'
run_remote kernel_config 'if [ -r /proc/config.gz ]; then toybox gzip -dc /proc/config.gz; else echo CONFIG_NOT_READABLE_OR_ABSENT; exit 4; fi'
run_remote dmesg_readonly 'dmesg 2>&1'
run_remote cmdq_strings 'for p in /vendor/lib/modules /system/lib/modules /system/vendor/lib/modules; do find "$p" -maxdepth 2 -type f 2>/dev/null | grep -Ei "cmdq|gce|mdp" || true; done'

find "$OUTPUT" -type f -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
cat > "$OUTPUT/result.md" <<EOF
# Phase 5F CMDQ runtime metadata

- Test ID: $TEST_ID
- Serial: $SERIAL
- Timestamp UTC: $STAMP
- Read-only: yes
- Device node open/ioctl: no
- Device mutation: no

This directory contains raw outputs and per-command exit codes. A failed
read-only command is retained as evidence of the shell/API boundary; it is not
interpreted as evidence about the kernel implementation without corroboration.
EOF
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote read-only CMDQ runtime capture to %s\n' "$OUTPUT"
