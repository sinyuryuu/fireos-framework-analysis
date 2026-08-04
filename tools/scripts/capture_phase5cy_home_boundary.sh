#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: capture_phase5cy_home_boundary.sh --serial SERIAL --output DIR [--dry-run]"
  echo "Read-only HOME/OOBE/test-state capture; refuses to overwrite output."
}

SERIAL=""
OUTPUT=""
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --serial) SERIAL="${2:-}"; shift 2 ;;
    --output) OUTPUT="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$SERIAL" || -z "$OUTPUT" ]]; then
  usage >&2
  exit 2
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  printf '%s\n' \
    "DRY-RUN: no device or filesystem changes" \
    "adb -s $SERIAL shell cmd package resolve-activity --brief -a MAIN -c HOME" \
    "adb -s $SERIAL shell dumpsys package preferred-activities" \
    "adb -s $SERIAL shell dumpsys activity activities" \
    "adb -s $SERIAL shell dumpsys activity recents" \
    "adb -s $SERIAL shell dumpsys window windows" \
    "adb -s $SERIAL shell pm list packages -f" \
    "adb -s $SERIAL shell settings get secure device_provisioned" \
    "adb -s $SERIAL shell settings get secure user_setup_complete"
  exit 0
fi

if [[ -e "$OUTPUT" ]]; then
  echo "Refusing to overwrite existing output: $OUTPUT" >&2
  exit 2
fi
command -v adb >/dev/null || { echo "adb not found" >&2; exit 2; }
mkdir -p "$OUTPUT"
adb_cmd() { adb -s "$SERIAL" "$@"; }
if ! adb_cmd get-state 2>/dev/null | grep -qx device; then
  echo "Serial is not connected in device state: $SERIAL" >&2
  exit 3
fi

date -u +%Y-%m-%dT%H:%M:%SZ > "$OUTPUT/timestamp_utc.txt"
{
  echo "scope=read-only"
  echo "serial=$SERIAL"
  echo "adb -s $SERIAL shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"
  echo "adb -s $SERIAL shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME"
  echo "adb -s $SERIAL shell dumpsys package preferred-activities"
  echo "adb -s $SERIAL shell dumpsys activity activities"
  echo "adb -s $SERIAL shell dumpsys activity recents"
  echo "adb -s $SERIAL shell dumpsys window windows"
  echo "adb -s $SERIAL shell pm list packages -f"
  echo "adb -s $SERIAL shell settings get secure device_provisioned"
  echo "adb -s $SERIAL shell settings get secure user_setup_complete"
} > "$OUTPUT/commands.txt"

adb_cmd devices -l > "$OUTPUT/adb-devices.txt"
adb_cmd shell getprop > "$OUTPUT/getprop.txt"
adb_cmd shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME > "$OUTPUT/home-resolve.txt" 2>&1 || true
adb_cmd shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME > "$OUTPUT/home-candidates.txt" 2>&1 || true
adb_cmd shell dumpsys package preferred-activities > "$OUTPUT/preferred-activities.txt" 2>&1 || true
adb_cmd shell dumpsys activity activities > "$OUTPUT/activity-activities.txt" 2>&1 || true
adb_cmd shell dumpsys activity recents > "$OUTPUT/activity-recents.txt" 2>&1 || true
adb_cmd shell dumpsys window windows > "$OUTPUT/window-windows.txt" 2>&1 || true
adb_cmd shell pm list packages -f > "$OUTPUT/package-list.txt" 2>&1 || true
{
  for key in device_provisioned user_setup_complete; do
    echo "=== secure $key"
    adb_cmd shell settings get secure "$key" 2>&1 || true
  done
  for key in boot_count user_setup_complete; do
    echo "=== global $key"
    adb_cmd shell settings get global "$key" 2>&1 || true
  done
} > "$OUTPUT/setup-settings.txt"
{
  echo '=== Fire Launcher'
  adb_cmd shell dumpsys package com.amazon.firelauncher 2>&1 || true
  echo '=== Phase 4 alias package'
  adb_cmd shell dumpsys package org.fireosresearch.phase4.alias 2>&1 || true
  echo '=== OOBE package'
  adb_cmd shell dumpsys package com.amazon.kindle.otter.oobe 2>&1 || true
} > "$OUTPUT/package-focus.txt"

{
  echo "observed_resolver=$(tr '\n' ' ' < "$OUTPUT/home-resolve.txt")"
  echo "phase4_alias_present=$(grep -c 'org.fireosresearch.phase4.alias' "$OUTPUT/package-list.txt" || true)"
  echo "firelauncher_present=$(grep -c 'com.amazon.firelauncher' "$OUTPUT/package-list.txt" || true)"
  echo "scope=read-only; no package state, settings, foreground, reboot, or process mutation"
} > "$OUTPUT/result.md"
(cd "$OUTPUT" && shasum -a 256 * > sha256sums.txt)
echo "Wrote read-only HOME boundary capture to $OUTPUT"
