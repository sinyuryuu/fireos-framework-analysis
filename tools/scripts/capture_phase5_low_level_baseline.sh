#!/usr/bin/env bash
# Capture a read-only low-level inventory for Phase 5.
#
# This script never reboots, enters bootloader mode, unlocks, remounts, flashes,
# writes a partition, invokes an exploit, or changes Android state. The output
# directory must be new so that prior evidence cannot be overwritten.

set -Eeuo pipefail

SERIAL=""
TEST_ID=""
OUTPUT=""
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  capture_phase5_low_level_baseline.sh --serial SERIAL --test-id ID --output DIR [--dry-run]

The serial is mandatory. The collection is observational only and does not
enter bootloader mode or execute fastboot against the device.
EOF
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --test-id) [ "$#" -ge 2 ] || die '--test-id requires a value'; TEST_ID="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$OUTPUT" ] || die '--output is required'

ADB=(adb -s "$SERIAL")

commands=(
  "${ADB[*]} devices -l"
  "${ADB[*]} get-state"
  "${ADB[*]} shell id"
  "${ADB[*]} shell getprop"
  "${ADB[*]} shell getenforce"
  "${ADB[*]} shell uname -a"
  "${ADB[*]} shell cat /proc/version"
  "${ADB[*]} shell cat /proc/cmdline"
  "${ADB[*]} shell cat /proc/bootconfig"
  "${ADB[*]} shell cat /proc/partitions"
  "${ADB[*]} shell ls -la /dev/block/by-name"
  "${ADB[*]} shell mount"
  "${ADB[*]} shell cat /proc/mounts"
  "${ADB[*]} shell getprop ro.product.model"
  "${ADB[*]} shell getprop ro.product.device"
  "${ADB[*]} shell getprop ro.build.fingerprint"
  "${ADB[*]} shell getprop ro.build.version.incremental"
  "${ADB[*]} shell getprop ro.build.version.security_patch"
  "${ADB[*]} shell getprop ro.build.version.fireos"
  "${ADB[*]} shell getprop ro.board.platform"
  "${ADB[*]} shell getprop ro.boot.hardware"
  "${ADB[*]} shell getprop ro.boot.flash.locked"
  "${ADB[*]} shell getprop ro.boot.verifiedbootstate"
  "${ADB[*]} shell getprop ro.boot.unlocked_kernel"
  "${ADB[*]} shell getprop ro.boot.rpmb_state"
  "${ADB[*]} shell getprop ro.boot.selinux"
  "${ADB[*]} shell getprop ro.boot.mode"
  "${ADB[*]} shell getprop ro.boot.bootreason"
  "${ADB[*]} shell getprop ro.bootloader"
  "${ADB[*]} shell pm path com.amazon.firelauncher"
  "${ADB[*]} shell dumpsys package com.amazon.firelauncher"
  "${ADB[*]} shell ps -A -o USER,PID,PPID,NAME,ARGS"
  "${ADB[*]} shell ls -la /system/etc/init"
  "${ADB[*]} shell ls -la /vendor/etc/init"
  "${ADB[*]} shell ls -la /system/etc/fosinit"
  "${ADB[*]} shell ls -la /vendor/etc/fosinit"
  "fastboot --version"
  "fastboot devices"
)

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no command will execute.\n'
  printf 'DRY-RUN: output=%s test-id=%s serial=%s\n' "$OUTPUT" "$TEST_ID" "$SERIAL"
  printf 'DRY-RUN: planned read-only commands:\n'
  printf '  %s\n' "${commands[@]}"
  exit 0
fi

case "$OUTPUT" in
  /|.|..|"") die "refusing unsafe output directory: $OUTPUT" ;;
esac
[ ! -e "$OUTPUT" ] || die "output directory already exists; refusing to overwrite: $OUTPUT"
mkdir -p "$OUTPUT/adb" "$OUTPUT/device" "$OUTPUT/boot" "$OUTPUT/storage" "$OUTPUT/paths" "$OUTPUT/tools"

printf 'test_id=%s\nserial=%s\ntimestamp_utc=%s\n' \
  "$TEST_ID" "$SERIAL" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.tsv"
printf '%s\n' "${commands[@]}" > "$OUTPUT/commands.txt"

run_capture() {
  local label="$1"
  shift
  local base="$OUTPUT/$label"
  mkdir -p "$(dirname "$base")"
  {
    printf 'command: '
    printf '%q ' "$@"
    printf '\n'
  } > "$base.command.txt"
  set +e
  "$@" > "$base.stdout.txt" 2> "$base.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$base.exit_code.txt"
}

run_capture adb/devices "${ADB[@]}" devices -l
if ! awk -v serial="$SERIAL" '$1 == serial && $2 == "device" { found=1 } END { exit(found ? 0 : 1) }' \
    "$OUTPUT/adb/devices.stdout.txt"; then
  die "serial is not connected in device state; see $OUTPUT/adb/devices.stdout.txt"
fi

run_capture adb/get_state "${ADB[@]}" get-state
run_capture device/id "${ADB[@]}" shell id
run_capture device/getprop "${ADB[@]}" shell getprop
run_capture device/getenforce "${ADB[@]}" shell getenforce
run_capture device/uname "${ADB[@]}" shell uname -a
run_capture device/proc_version "${ADB[@]}" shell cat /proc/version
run_capture boot/proc_cmdline "${ADB[@]}" shell cat /proc/cmdline
run_capture boot/proc_bootconfig "${ADB[@]}" shell cat /proc/bootconfig
run_capture storage/proc_partitions "${ADB[@]}" shell cat /proc/partitions
run_capture paths/block_by_name "${ADB[@]}" shell ls -la /dev/block/by-name
run_capture storage/mount "${ADB[@]}" shell mount
run_capture storage/proc_mounts "${ADB[@]}" shell cat /proc/mounts

run_capture device/model "${ADB[@]}" shell getprop ro.product.model
run_capture device/product "${ADB[@]}" shell getprop ro.product.device
run_capture device/fingerprint "${ADB[@]}" shell getprop ro.build.fingerprint
run_capture device/incremental "${ADB[@]}" shell getprop ro.build.version.incremental
run_capture device/security_patch "${ADB[@]}" shell getprop ro.build.version.security_patch
run_capture device/fireos "${ADB[@]}" shell getprop ro.build.version.fireos
run_capture device/board_platform "${ADB[@]}" shell getprop ro.board.platform
run_capture device/boot_hardware "${ADB[@]}" shell getprop ro.boot.hardware
run_capture boot/flash_locked "${ADB[@]}" shell getprop ro.boot.flash.locked
run_capture boot/verifiedbootstate "${ADB[@]}" shell getprop ro.boot.verifiedbootstate
run_capture boot/unlocked_kernel "${ADB[@]}" shell getprop ro.boot.unlocked_kernel
run_capture boot/rpmb_state "${ADB[@]}" shell getprop ro.boot.rpmb_state
run_capture boot/selinux "${ADB[@]}" shell getprop ro.boot.selinux
run_capture boot/mode "${ADB[@]}" shell getprop ro.boot.mode
run_capture boot/bootreason "${ADB[@]}" shell getprop ro.boot.bootreason
run_capture boot/bootloader "${ADB[@]}" shell getprop ro.bootloader

run_capture device/firelauncher_path "${ADB[@]}" shell pm path com.amazon.firelauncher
run_capture device/firelauncher_package "${ADB[@]}" shell dumpsys package com.amazon.firelauncher
run_capture device/processes "${ADB[@]}" shell ps -A -o USER,PID,PPID,NAME,ARGS
run_capture paths/system_init "${ADB[@]}" shell ls -la /system/etc/init
run_capture paths/vendor_init "${ADB[@]}" shell ls -la /vendor/etc/init
run_capture paths/system_fosinit "${ADB[@]}" shell ls -la /system/etc/fosinit
run_capture paths/vendor_fosinit "${ADB[@]}" shell ls -la /vendor/etc/fosinit

run_capture tools/fastboot_version fastboot --version
run_capture tools/fastboot_devices fastboot devices

if command -v shasum >/dev/null 2>&1; then
  find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
else
  die 'shasum is required to create the evidence manifest'
fi

{
  printf '# Phase 5 low-level read-only baseline\n\n'
  printf '%s\n' "- Test ID: $TEST_ID"
  printf '%s\n' "- Serial: $SERIAL"
  printf '%s\n' "- Timestamp UTC: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  printf '%s\n' '- No reboot, bootloader transition, exploit, remount, partition write, or Android-state mutation was executed.'
  printf '%s\n' '- Host fastboot version/device enumeration are recorded only; the tablet remained in Android ADB device mode.'
  printf '%s\n' '- Individual command failures are preserved in *.exit_code.txt and are not silently treated as absence.'
  printf '%s\n' '- SHA-256 manifest: sha256sums.txt'
} > "$OUTPUT/summary.md"

printf 'Captured Phase 5 low-level read-only baseline in %s\n' "$OUTPUT"
