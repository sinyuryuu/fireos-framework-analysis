#!/usr/bin/env bash
# Capture a fresh, read-only PS7331 state snapshot.
# This script contains no package/settings/Binder/driver/OTA/reboot mutation.
set -euo pipefail

SERIAL=""
OUTPUT=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --serial) SERIAL="${2:?missing serial}"; shift 2 ;;
    --output) OUTPUT="${2:?missing output directory}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$SERIAL" || -z "$OUTPUT" ]]; then
  echo "usage: $0 --serial DEVICE_SERIAL --output OUTPUT_DIR [--dry-run]" >&2
  exit 2
fi

commands=(
  "adb -s $SERIAL get-state"
  "adb -s $SERIAL shell getprop"
  "adb -s $SERIAL shell sh -c 'getenforce; id; cat /proc/version; uname -a'"
  "adb -s $SERIAL shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"
  "adb -s $SERIAL shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME"
  "adb -s $SERIAL shell dumpsys package preferred-activities"
  "adb -s $SERIAL shell dumpsys package com.amazon.firelauncher"
  "adb -s $SERIAL shell dumpsys activity activities"
  "adb -s $SERIAL shell dumpsys window windows"
  "adb -s $SERIAL shell pm list users"
  "adb -s $SERIAL shell dumpsys role"
  "adb -s $SERIAL shell dumpsys device_policy"
  "adb -s $SERIAL shell service list"
  "adb -s $SERIAL shell cmd overlay list"
  "adb -s $SERIAL shell settings list system"
  "adb -s $SERIAL shell settings list secure"
  "adb -s $SERIAL shell settings list global"
)

if [[ "$DRY_RUN" == 1 ]]; then
  printf '%s\n' "dry-run: no directory will be created and no command will run"
  printf '%s\n' "serial=$SERIAL" "output=$OUTPUT"
  printf '%s\n' "${commands[@]}"
  exit 0
fi

if [[ -e "$OUTPUT" ]]; then
  echo "refusing to overwrite existing evidence directory: $OUTPUT" >&2
  exit 3
fi
mkdir -p "$OUTPUT"
printf '%s\n' "serial=$SERIAL" "captured_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OUTPUT/metadata.txt"
printf '%s\n' "${commands[@]}" > "$OUTPUT/commands.txt"

capture() {
  local name="$1"
  shift
  "$@" > "$OUTPUT/${name}.stdout.txt" 2> "$OUTPUT/${name}.stderr.txt"
  local rc=$?
  printf '%s\n' "$rc" > "$OUTPUT/${name}.rc.txt"
  printf '%s\t%s\n' "$name" "$rc" >> "$OUTPUT/command-results.tsv"
  return 0
}

capture adb_state adb -s "$SERIAL" get-state
capture target_id adb -s "$SERIAL" shell getprop
capture security_state adb -s "$SERIAL" shell sh -c 'getenforce; id; cat /proc/version; uname -a'
capture home_resolve adb -s "$SERIAL" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
capture home_candidates adb -s "$SERIAL" shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME
capture preferred adb -s "$SERIAL" shell dumpsys package preferred-activities
capture firelauncher_package adb -s "$SERIAL" shell dumpsys package com.amazon.firelauncher
capture activity adb -s "$SERIAL" shell dumpsys activity activities
capture window adb -s "$SERIAL" shell dumpsys window windows
capture users adb -s "$SERIAL" shell pm list users
capture roles adb -s "$SERIAL" shell dumpsys role
capture device_policy adb -s "$SERIAL" shell dumpsys device_policy
capture services adb -s "$SERIAL" shell service list
capture overlay adb -s "$SERIAL" shell cmd overlay list
capture settings_system adb -s "$SERIAL" shell settings list system
capture settings_secure adb -s "$SERIAL" shell settings list secure
capture settings_global adb -s "$SERIAL" shell settings list global

( cd "$OUTPUT" && find . -maxdepth 1 -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 sha256sum > sha256sums.txt )
printf '%s\n' "$OUTPUT"
