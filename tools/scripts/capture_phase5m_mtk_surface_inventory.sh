#!/usr/bin/env bash
# Read-only MTK driver surface inventory for Phase 5M.
#
# This collector only lists device nodes, sysfs class entries, init/config
# filenames, services, processes, and properties. It never opens a device
# node, sends ioctl/HCI/Binder traffic, starts a service, changes a property,
# changes package state, reboots, enters bootloader mode, or writes storage.
set -Eeuo pipefail
export LC_ALL=C

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
      printf '%s\n' 'Usage: capture_phase5m_mtk_surface_inventory.sh --serial SERIAL --output DIR [--dry-run]'
      exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac

ADB=(adb -s "$SERIAL")
COMMANDS=(
  "${ADB[*]} get-state"
  "${ADB[*]} shell id"
  "${ADB[*]} shell getprop"
  "${ADB[*]} shell getenforce"
  "${ADB[*]} shell service list"
  "${ADB[*]} shell ps -A -o USER,PID,PPID,NAME,ARGS"
  "${ADB[*]} shell ls -laZ /dev"
  "${ADB[*]} shell find /dev -maxdepth 1 -type c -ls"
  "${ADB[*]} shell ls -laZ /sys/class/misc"
  "${ADB[*]} shell ls -laZ /sys/class/uio"
  "${ADB[*]} shell ls -laZ /sys/class/video4linux"
  "${ADB[*]} shell ls -laZ /sys/class/bluetooth"
  "${ADB[*]} shell find /vendor/etc/init /system/etc/init -maxdepth 2 -type f"
  "${ADB[*]} shell find /vendor/bin /system/bin /system/xbin -maxdepth 2 -type f"
  "${ADB[*]} shell find /vendor/lib /vendor/lib64 /system/lib /system/lib64 -maxdepth 3 -type f"
  "${ADB[*]} shell ls -laZ /vendor/lib/modules"
  "${ADB[*]} shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"
)

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no command will execute; no device node will be opened.\n'
  printf 'DRY-RUN: serial=%s output=%s\n' "$SERIAL" "$OUTPUT"
  printf '%s\n' "${COMMANDS[@]}"
  exit 0
fi

command -v adb >/dev/null 2>&1 || die 'adb is required'
command -v shasum >/dev/null 2>&1 || die 'shasum is required'
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"
mkdir -p "$OUTPUT"

printf 'test_id=%s\nserial=%s\nstart_utc=%s\nmode=read-only\n' \
  "$(basename "$OUTPUT")" "$SERIAL" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.txt"
printf '%s\n' "${COMMANDS[@]}" > "$OUTPUT/commands.txt"

run_capture() {
  local name="$1"; shift
  local status
  set +e
  "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  status="$?"
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
}

run_capture device.get-state "${ADB[@]}" get-state
if ! grep -qx 'device' "$OUTPUT/device.get-state.stdout.txt"; then
  die "serial is not in ADB device state; see $OUTPUT/device.get-state.stdout.txt"
fi
run_capture device.id "${ADB[@]}" shell id
run_capture device.getprop "${ADB[@]}" shell getprop
run_capture device.getenforce "${ADB[@]}" shell getenforce
run_capture device.services "${ADB[@]}" shell service list
run_capture device.processes "${ADB[@]}" shell ps -A -o USER,PID,PPID,NAME,ARGS
run_capture surface.dev "${ADB[@]}" shell ls -laZ /dev
run_capture surface.dev-character "${ADB[@]}" shell find /dev -maxdepth 1 -type c -ls
run_capture surface.class-misc "${ADB[@]}" shell ls -laZ /sys/class/misc
run_capture surface.class-uio "${ADB[@]}" shell ls -laZ /sys/class/uio
run_capture surface.class-video4linux "${ADB[@]}" shell ls -laZ /sys/class/video4linux
run_capture surface.class-bluetooth "${ADB[@]}" shell ls -laZ /sys/class/bluetooth
run_capture paths.init "${ADB[@]}" shell find /vendor/etc/init /system/etc/init -maxdepth 2 -type f
run_capture paths.bin "${ADB[@]}" shell find /vendor/bin /system/bin /system/xbin -maxdepth 2 -type f
run_capture paths.lib "${ADB[@]}" shell find /vendor/lib /vendor/lib64 /system/lib /system/lib64 -maxdepth 3 -type f
run_capture paths.modules "${ADB[@]}" shell ls -laZ /vendor/lib/modules
run_capture device.home "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME

rg -i 'sram|genie|gz|ccci|vcu|apu|cmdq|ion|m4u|vcodec|mdp|mtk|bluetooth|hci|wmt' \
  "$OUTPUT/surface.dev.stdout.txt" "$OUTPUT/surface.dev-character.stdout.txt" \
  "$OUTPUT/surface.class-misc.stdout.txt" "$OUTPUT/surface.class-uio.stdout.txt" \
  "$OUTPUT/surface.class-video4linux.stdout.txt" "$OUTPUT/surface.class-bluetooth.stdout.txt" \
  "$OUTPUT/paths.init.stdout.txt" "$OUTPUT/paths.bin.stdout.txt" "$OUTPUT/paths.lib.stdout.txt" \
  > "$OUTPUT/filtered-mtk-surface.txt" || true

printf 'end_utc=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$OUTPUT/metadata.txt"
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
