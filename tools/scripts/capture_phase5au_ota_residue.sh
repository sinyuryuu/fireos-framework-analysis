#!/usr/bin/env bash
set -Eeuo pipefail

# Capture OTA/update residue using read-only shell commands.
# The optional dashboard probe only attempts to launch an exported debug UI;
# it does not send check/download/install commands. A Home key is sent after
# that probe solely to restore the foreground launcher.

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
SERIAL=""
OUTPUT=""
DRY_RUN=0
PROBE_DASHBOARD=0

usage() {
  cat <<'EOF'
Usage:
  capture_phase5au_ota_residue.sh --serial SERIAL --output DIR [--probe-dashboard] [--dry-run]

The script requires an explicit ADB serial and refuses to overwrite output.
Default commands are read-only. --probe-dashboard attempts only the OTA
debug activity and then sends KEYCODE_HOME to restore the foreground launcher.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || { echo '--serial requires a value' >&2; exit 2; }; SERIAL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || { echo '--output requires a value' >&2; exit 2; }; OUTPUT="$2"; shift 2 ;;
    --probe-dashboard) PROBE_DASHBOARD=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[ -n "$SERIAL" ] || { echo '--serial is required' >&2; exit 2; }
[ -n "$OUTPUT" ] || { echo '--output is required' >&2; exit 2; }
case "$OUTPUT" in
  /|.|..|"$PROJECT_ROOT"|"$PROJECT_ROOT/"*) echo 'unsafe output path' >&2; exit 2 ;;
esac
[ ! -e "$OUTPUT" ] || { echo "refusing to overwrite existing output: $OUTPUT" >&2; exit 2; }

timestamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
print_cmd() { printf '%q ' "$@"; printf '\n'; }

if [ "$DRY_RUN" -eq 1 ]; then
  cat <<EOF
serial=$SERIAL
output=$OUTPUT
read-only capture commands:
  adb -s $SERIAL get-state
  adb -s $SERIAL shell getprop
  adb -s $SERIAL shell dumpsys package com.amazon.device.software.ota
  adb -s $SERIAL shell pm list packages
  adb -s $SERIAL shell ls -la /cache/recovery
  adb -s $SERIAL shell cat /cache/recovery/last_log
  adb -s $SERIAL shell cat /cache/recovery/last_install
  adb -s $SERIAL shell dumpsys
  adb -s $SERIAL shell settings list system|secure|global
  adb -s $SERIAL shell service list
  adb -s $SERIAL shell dumpsys system_update|otadexopt|updatelock|webviewupdate
  adb -s $SERIAL shell dumpsys package com.amazon.settings.systemupdates
EOF
  if [ "$PROBE_DASHBOARD" -eq 1 ]; then
    cat <<EOF
optional foreground-only probe:
  adb -s $SERIAL shell am start -W -n com.amazon.device.software.ota/.dx.OtaDashboardActivity
  adb -s $SERIAL shell input keyevent 3
EOF
  fi
  exit 0
fi

mkdir -p "$OUTPUT"
printf 'test_id\tPHASE5AU-OTA-RESIDUE\nserial\t%s\ntimestamp_utc\t%s\nprobe_dashboard\t%s\n' \
  "$SERIAL" "$(timestamp)" "$PROBE_DASHBOARD" > "$OUTPUT/metadata.tsv"

run_capture() {
  local name="$1"
  shift
  print_cmd "$@" > "$OUTPUT/$name.command.txt"
  set +e
  "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
  return 0
}

run_capture device_state adb -s "$SERIAL" get-state
if [ "$(tr -d '\r\n' < "$OUTPUT/device_state.stdout.txt")" != "device" ]; then
  echo "selected serial is not in device state: $SERIAL" >&2
  exit 3
fi
run_capture getprop_full adb -s "$SERIAL" shell getprop
rg -i 'ro\.build|amazon|ota|update|product|device' "$OUTPUT/getprop_full.stdout.txt" > "$OUTPUT/getprop_filtered.txt" || true
run_capture dumpsys_package_ota adb -s "$SERIAL" shell dumpsys package com.amazon.device.software.ota
run_capture pm_list_packages adb -s "$SERIAL" shell pm list packages
rg -i 'ota|update|dcp|software' "$OUTPUT/pm_list_packages.stdout.txt" > "$OUTPUT/pm_list_packages_filtered.txt" || true
run_capture pm_path_ota adb -s "$SERIAL" shell pm path com.amazon.device.software.ota

for target in \
  /cache /cache/recovery /data/cache /data/ota /data/ota_package \
  /data/update_engine /data/update_engine_log /data/misc/update_engine \
  /data/misc/ota /data/system/update_engine \
  /data/user/0/com.amazon.device.software.ota \
  /data/data/com.amazon.device.software.ota /sdcard/Download /sdcard \
  /data/media/0/Download /data/local/tmp; do
  name=$(printf '%s' "$target" | sed 's#^/##; s#[^A-Za-z0-9_]#_#g')
  run_capture "path_$name" adb -s "$SERIAL" shell ls -la "$target"
done

for pair in \
  'cache:/cache' 'data-cache:/data/cache' 'data-ota:/data/ota' \
  'data-misc:/data/misc' 'data-media:/data/media/0' 'sdcard:/sdcard'; do
  label=$(printf '%s' "$pair" | cut -d: -f1)
  target=$(printf '%s' "$pair" | cut -d: -f2-)
  run_capture "find_$label" adb -s "$SERIAL" shell find "$target" -maxdepth 2 -type f \
    \( -iname '*ota*' -o -iname '*update*' -o -iname '*PS7330*' \
       -o -iname '*PS7331*' -o -iname '*kindle*' -o -iname '*.bin' -o -iname '*.zip' \) -print
done

for namespace in system secure global; do
  run_capture "settings_$namespace" adb -s "$SERIAL" shell settings list "$namespace"
  rg -i 'ota|update|build|fireos|amazon|device|product|download|recovery' \
    "$OUTPUT/settings_$namespace.stdout.txt" > "$OUTPUT/settings_$namespace""_filtered.txt" || true
done

run_capture service_list adb -s "$SERIAL" shell service list
rg -i 'ota|update|recovery|download|dcp|software' "$OUTPUT/service_list.stdout.txt" > "$OUTPUT/service_list_filtered.txt" || true
for service in system_update otadexopt updatelock webviewupdate; do
  run_capture "dumpsys_$service" adb -s "$SERIAL" shell dumpsys "$service"
done
run_capture dumpsys_package_systemupdates adb -s "$SERIAL" shell dumpsys package com.amazon.settings.systemupdates
run_capture dumpsys_activity_services_ota adb -s "$SERIAL" shell dumpsys activity services com.amazon.device.software.ota
run_capture dumpsys_all adb -s "$SERIAL" shell dumpsys
rg -i 'ota|update|PS7330' "$OUTPUT/dumpsys_all.stdout.txt" > "$OUTPUT/dumpsys_filtered.txt" || true

if [ "$PROBE_DASHBOARD" -eq 1 ]; then
  run_capture dashboard_before_activity adb -s "$SERIAL" shell dumpsys activity activities
  run_capture dashboard_before_window adb -s "$SERIAL" shell dumpsys window windows
  run_capture dashboard_start adb -s "$SERIAL" shell am start -W -n com.amazon.device.software.ota/.dx.OtaDashboardActivity
  sleep 2
  run_capture dashboard_after_activity adb -s "$SERIAL" shell dumpsys activity activities
  run_capture dashboard_after_window adb -s "$SERIAL" shell dumpsys window windows
  run_capture dashboard_ui adb -s "$SERIAL" shell uiautomator dump /dev/tty
  run_capture dashboard_restore_home adb -s "$SERIAL" shell input keyevent 3
  sleep 1
  run_capture dashboard_restored_activity adb -s "$SERIAL" shell dumpsys activity activities
  run_capture dashboard_restored_window adb -s "$SERIAL" shell dumpsys window windows
fi

(cd "$PROJECT_ROOT" && find "$OUTPUT" -type f ! -name 'sha256sums.final.txt' -print0 | sort -z | xargs -0 shasum -a 256) > "$OUTPUT/sha256sums.final.txt"
printf 'capture complete: %s\n' "$OUTPUT"
