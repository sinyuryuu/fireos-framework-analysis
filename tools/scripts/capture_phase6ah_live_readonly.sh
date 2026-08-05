#!/usr/bin/env bash
set -u

# Phase 6AH live verification is intentionally read-only. It never invokes
# update-binary, recovery, OTA installation, reboot, settings mutation, or a
# Binder transaction with an unknown code.

usage() {
  echo "Usage: $0 --serial DEVICE_SERIAL --output OUTPUT_DIR [--dry-run]" >&2
}

SERIAL=""
OUTPUT=""
DRY_RUN=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) SERIAL="${2:-}"; shift 2 ;;
    --output) OUTPUT="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [ -z "$SERIAL" ] || [ -z "$OUTPUT" ]; then
  usage
  exit 2
fi

if ! command -v adb >/dev/null 2>&1; then
  echo "ERROR: adb is not installed or not on PATH" >&2
  exit 2
fi

if [ "$DRY_RUN" -eq 1 ]; then
  echo "DRY_RUN: read-only commands only; no output written"
  printf '%s\n' \
    "adb -s $SERIAL get-state" \
    "adb -s $SERIAL shell getprop" \
    "adb -s $SERIAL shell id" \
    "adb -s $SERIAL shell getenforce" \
    "adb -s $SERIAL shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME" \
    "adb -s $SERIAL shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME" \
    "adb -s $SERIAL shell dumpsys package com.amazon.firelauncher" \
    "adb -s $SERIAL shell dumpsys package preferred-activities" \
    "adb -s $SERIAL shell dumpsys activity activities" \
    "adb -s $SERIAL shell dumpsys window windows" \
    "adb -s $SERIAL shell dumpsys update_engine" \
    "adb -s $SERIAL shell cmd otadexopt help" \
    "adb -s $SERIAL shell cmd otadexopt progress" \
    "adb -s $SERIAL shell cmd otadexopt done" \
    "adb -s $SERIAL shell dumpsys system_update" \
    "adb -s $SERIAL shell dumpsys package com.amazon.device.software.ota" \
    "adb -s $SERIAL shell dumpsys package com.amazon.device.software.ota.override" \
    "adb -s $SERIAL shell dumpsys package com.amazon.settings.systemupdates" \
    "adb -s $SERIAL shell pm path com.amazon.device.software.ota" \
    "adb -s $SERIAL shell pm path com.amazon.device.software.ota.override" \
    "adb -s $SERIAL shell pm path com.amazon.settings.systemupdates" \
    "adb -s $SERIAL shell service list" \
    "adb -s $SERIAL shell cmd overlay list" \
    "adb -s $SERIAL shell dumpsys role" \
    "adb -s $SERIAL shell dumpsys device_policy" \
    "adb -s $SERIAL shell appops get com.amazon.firelauncher" \
    "adb -s $SERIAL shell pm path com.amazon.firelauncher" \
    "adb -s $SERIAL shell pm list packages -f" \
    "adb -s $SERIAL shell cat /proc/cmdline" \
    "adb -s $SERIAL shell cat /proc/mounts" \
    "adb -s $SERIAL shell ls -la /cache/recovery" \
    "adb -s $SERIAL shell cat /cache/recovery/last_log" \
    "adb -s $SERIAL shell cat /cache/recovery/last_install" \
    "adb -s $SERIAL logcat -d -b all -v threadtime -t 500"
  exit 0
fi

if [ -e "$OUTPUT" ]; then
  echo "ERROR: refusing to overwrite existing output directory: $OUTPUT" >&2
  exit 2
fi
mkdir -p "$OUTPUT"

DEVICES="$(adb devices -l 2>&1)"
printf '%s\n' "$DEVICES" > "$OUTPUT/adb_devices.txt"
MATCH="$(printf '%s\n' "$DEVICES" | awk -v serial="$SERIAL" '$1 == serial && $2 == "device" { print $1 }')"
if [ "$MATCH" != "$SERIAL" ]; then
  echo "ERROR: exact serial is not connected in device state: $SERIAL" >&2
  exit 3
fi

date -u +%Y-%m-%dT%H:%M:%SZ > "$OUTPUT/captured_at_utc.txt"
printf '%s\n' "$SERIAL" > "$OUTPUT/serial.txt"
printf '%s\n' "READ_ONLY=YES" "OTA_EXECUTED=NO" "RECOVERY_EXECUTED=NO" \
  "REBOOT=NO" "SETTINGS_MUTATION=NO" "UNKNOWN_BINDER_TRANSACTION=NO" \
  > "$OUTPUT/safety.txt"

run_adb() {
  local name="$1"
  shift
  local args=("$@")
  printf 'adb -s %q' "$SERIAL" >> "$OUTPUT/commands.txt"
  printf ' %q' "${args[@]}" >> "$OUTPUT/commands.txt"
  printf '\n' >> "$OUTPUT/commands.txt"
  adb -s "$SERIAL" "${args[@]}" > "$OUTPUT/${name}.stdout.txt" 2> "$OUTPUT/${name}.stderr.txt"
  printf '%s\n' "$?" > "$OUTPUT/${name}.returncode.txt"
}

run_adb get_state get-state
run_adb getprop shell getprop
run_adb identity shell id
run_adb selinux shell getenforce
run_adb home_resolve shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
run_adb home_candidates shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME
run_adb firelauncher_package shell dumpsys package com.amazon.firelauncher
run_adb preferred_activities shell dumpsys package preferred-activities
run_adb activity_activities shell dumpsys activity activities
run_adb window_windows shell dumpsys window windows
run_adb update_engine_dumpsys shell dumpsys update_engine
run_adb otadexopt_help shell cmd otadexopt help
run_adb otadexopt_progress shell cmd otadexopt progress
run_adb otadexopt_done shell cmd otadexopt done
run_adb system_update_dumpsys shell dumpsys system_update
run_adb ota_package_dumpsys shell dumpsys package com.amazon.device.software.ota
run_adb ota_override_dumpsys shell dumpsys package com.amazon.device.software.ota.override
run_adb settings_updates_dumpsys shell dumpsys package com.amazon.settings.systemupdates
run_adb ota_package_path shell pm path com.amazon.device.software.ota
run_adb ota_override_path shell pm path com.amazon.device.software.ota.override
run_adb settings_updates_path shell pm path com.amazon.settings.systemupdates
run_adb service_list shell service list
run_adb overlay_list shell cmd overlay list
run_adb role_dumpsys shell dumpsys role
run_adb device_policy_dumpsys shell dumpsys device_policy
run_adb firelauncher_appops shell appops get com.amazon.firelauncher
run_adb firelauncher_path shell pm path com.amazon.firelauncher
run_adb package_paths shell pm list packages -f
run_adb proc_cmdline shell cat /proc/cmdline
run_adb proc_mounts shell cat /proc/mounts
run_adb recovery_ls shell ls -la /cache/recovery
run_adb recovery_last_log shell cat /cache/recovery/last_log
run_adb recovery_last_install shell cat /cache/recovery/last_install
run_adb logcat_tail logcat -d -b all -v threadtime -t 500

if command -v sha256sum >/dev/null 2>&1; then
  # Do not include the manifest itself; otherwise its digest is self-referential
  # and cannot be verified after the file is written.
  find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 sha256sum > "$OUTPUT/sha256sums.txt"
fi

echo "Captured read-only Phase 6AH live verification in $OUTPUT"
