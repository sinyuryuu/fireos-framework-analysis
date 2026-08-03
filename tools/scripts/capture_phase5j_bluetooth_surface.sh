#!/usr/bin/env bash
# Read-only MT8183 Bluetooth/HCI surface capture for Phase 5J.
#
# This script only enumerates packages, services, processes, properties,
# dumpsys output, and shell-visible vendor paths.  It never enables Bluetooth,
# sends HCI traffic, changes AppOps/package state, starts a vendor daemon,
# invokes a Binder transaction, reboots, or enters a bootloader.
set -Eeuo pipefail

SERIAL=""
OUTPUT=""
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: capture_phase5j_bluetooth_surface.sh --serial SERIAL --output DIR [--dry-run]'
      exit 0
      ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac

if [ "$DRY_RUN" -eq 1 ]; then
  printf '%s\n' 'DRY-RUN: read-only Bluetooth manager, package, process, property, service, and vendor-path capture'
  printf 'DRY-RUN: serial=%s output=%s; no mutation command is present\n' "$SERIAL" "$OUTPUT"
  exit 0
fi

command -v adb >/dev/null 2>&1 || die 'adb is required'
command -v shasum >/dev/null 2>&1 || die 'shasum is required'
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"
mkdir -p "$OUTPUT"

printf 'test_id=%s\nserial=%s\nstart_utc=%s\nmode=read-only\n' \
  "$(basename "$OUTPUT")" "$SERIAL" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.txt"

run_capture() {
  local name="$1"
  local rc
  shift
  set +e
  "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  rc="$?"
  set -e
  printf '%s\n' "$rc" > "$OUTPUT/$name.exit_code.txt"
}

cat > "$OUTPUT/commands.txt" <<EOF
adb -s $SERIAL get-state
adb -s $SERIAL shell id
adb -s $SERIAL shell getprop
adb -s $SERIAL shell getenforce
adb -s $SERIAL shell service list
adb -s $SERIAL shell ps -A -o USER,PID,PPID,NAME,ARGS
adb -s $SERIAL shell pm list packages -f
adb -s $SERIAL shell pm path com.android.bluetooth
adb -s $SERIAL shell dumpsys bluetooth_manager
adb -s $SERIAL shell dumpsys package com.android.bluetooth
adb -s $SERIAL shell dumpsys activity services
adb -s $SERIAL shell dumpsys meminfo com.android.bluetooth
adb -s $SERIAL shell ls -la /dev | grep -i bluetooth
adb -s $SERIAL shell ls -la /dev | grep -i hci
adb -s $SERIAL shell ls -la /sys/class/bluetooth
adb -s $SERIAL shell find /vendor/etc -maxdepth 3 -type f
adb -s $SERIAL shell find /vendor/bin -maxdepth 2 -type f
adb -s $SERIAL shell find /vendor/lib -maxdepth 3 -type f
adb -s $SERIAL shell find /vendor/lib64 -maxdepth 3 -type f
adb -s $SERIAL shell find /system/lib -maxdepth 3 -type f
adb -s $SERIAL shell find /system/lib64 -maxdepth 3 -type f
adb -s $SERIAL shell ls -la /vendor/lib/modules
adb -s $SERIAL shell cat /vendor/etc/init/init.bt_drv.rc
adb -s $SERIAL shell cat /vendor/etc/init/init.wmt_drv.rc
adb -s $SERIAL shell cat /vendor/etc/init/btmac.rc
adb -s $SERIAL shell cat /vendor/etc/init/android.hardware.bluetooth@1.0-service-mediatek.rc
adb -s $SERIAL shell dumpsys hwservicemanager
adb -s $SERIAL shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
EOF

run_capture device.get-state adb -s "$SERIAL" get-state
run_capture device.id adb -s "$SERIAL" shell id
run_capture device.getprop adb -s "$SERIAL" shell getprop
run_capture device.getenforce adb -s "$SERIAL" shell getenforce
run_capture device.service-list adb -s "$SERIAL" shell service list
run_capture device.processes adb -s "$SERIAL" shell ps -A -o USER,PID,PPID,NAME,ARGS
run_capture device.packages adb -s "$SERIAL" shell pm list packages -f
run_capture device.bluetooth-path adb -s "$SERIAL" shell pm path com.android.bluetooth
run_capture device.bluetooth-manager adb -s "$SERIAL" shell dumpsys bluetooth_manager
run_capture device.bluetooth-package adb -s "$SERIAL" shell dumpsys package com.android.bluetooth
run_capture device.activity-services adb -s "$SERIAL" shell dumpsys activity services
run_capture device.bluetooth-meminfo adb -s "$SERIAL" shell dumpsys meminfo com.android.bluetooth
run_capture paths.dev-bluetooth adb -s "$SERIAL" shell sh -c 'ls -la /dev | grep -i bluetooth'
run_capture paths.dev-hci adb -s "$SERIAL" shell sh -c 'ls -la /dev | grep -i hci'
run_capture paths.sys-bluetooth adb -s "$SERIAL" shell ls -la /sys/class/bluetooth
run_capture paths.vendor-etc adb -s "$SERIAL" shell find /vendor/etc -maxdepth 3 -type f
run_capture paths.vendor-bin adb -s "$SERIAL" shell find /vendor/bin -maxdepth 2 -type f
run_capture paths.vendor-lib adb -s "$SERIAL" shell find /vendor/lib -maxdepth 3 -type f
run_capture paths.vendor-lib64 adb -s "$SERIAL" shell find /vendor/lib64 -maxdepth 3 -type f
run_capture paths.system-lib adb -s "$SERIAL" shell find /system/lib -maxdepth 3 -type f
run_capture paths.system-lib64 adb -s "$SERIAL" shell find /system/lib64 -maxdepth 3 -type f
run_capture paths.vendor-modules adb -s "$SERIAL" shell ls -la /vendor/lib/modules
run_capture config.init-bt-driver adb -s "$SERIAL" shell cat /vendor/etc/init/init.bt_drv.rc
run_capture config.init-wmt-driver adb -s "$SERIAL" shell cat /vendor/etc/init/init.wmt_drv.rc
run_capture config.btmac adb -s "$SERIAL" shell cat /vendor/etc/init/btmac.rc
run_capture config.bluetooth-hal adb -s "$SERIAL" shell cat /vendor/etc/init/android.hardware.bluetooth@1.0-service-mediatek.rc
run_capture device.hwservicemanager adb -s "$SERIAL" shell dumpsys hwservicemanager
run_capture device.home adb -s "$SERIAL" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME

rg -i 'bluetooth|bluedroid|btif|hci|btuart|a2dp|gatt|avrcp|sco|vendor\.mediatek' \
  "$OUTPUT/device.packages.stdout.txt" "$OUTPUT/device.processes.stdout.txt" \
  "$OUTPUT/device.service-list.stdout.txt" "$OUTPUT/device.getprop.stdout.txt" \
  "$OUTPUT/paths.vendor-etc.stdout.txt" "$OUTPUT/paths.vendor-bin.stdout.txt" \
  "$OUTPUT/paths.vendor-lib.stdout.txt" "$OUTPUT/paths.vendor-lib64.stdout.txt" \
  "$OUTPUT/paths.system-lib.stdout.txt" "$OUTPUT/paths.system-lib64.stdout.txt" \
  > "$OUTPUT/filtered-bluetooth-surface.txt" || true

rg -i -n -C 3 'bluetooth|hci|a2dp|gatt|avrcp|sco|mediatek' \
  "$OUTPUT/device.bluetooth-manager.stdout.txt" \
  "$OUTPUT/device.bluetooth-package.stdout.txt" \
  "$OUTPUT/device.activity-services.stdout.txt" \
  > "$OUTPUT/filtered-bluetooth-dumps.txt" || true

printf 'end_utc=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$OUTPUT/metadata.txt"
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
