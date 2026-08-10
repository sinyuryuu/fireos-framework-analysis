#!/usr/bin/env bash
set -euo pipefail

# Read-only Phase 14 runtime capture. This script intentionally does not
# clear logcat, send a Binder transaction, start/stop an app, change settings,
# change package state, reboot, or touch a partition.

serial=""
output=""
dry_run=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --serial) serial="${2:?missing value for --serial}"; shift 2 ;;
    --output) output="${2:?missing value for --output}"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    --help|-h)
      sed -n '1,18p' "$0"
      exit 0
      ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ -n "$serial" ]] || { echo "--serial is required" >&2; exit 2; }
[[ -n "$output" ]] || { echo "--output is required" >&2; exit 2; }
[[ "$serial" != *" "* ]] || { echo "serial must be a single device serial" >&2; exit 2; }

if (( dry_run )); then
  printf '%s\n' "adb -s $serial get-state"
  printf '%s\n' "read-only captures: getprop, service list, selected dumpsys, HOME resolve, preferred-xml, logcat -d"
  printf '%s\n' "no output directory or device state will be changed"
  exit 0
fi

mkdir -p "$output"
adb=(adb -s "$serial")
[[ "$("${adb[@]}" get-state 2>/dev/null || true)" == "device" ]] || {
  echo "device is not in adb device state" >&2
  exit 3
}

timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '%s\n' "{\"serial\":\"$serial\",\"timestamp_utc\":\"$timestamp\",\"mutation\":false,\"scope\":\"read-only dumpsys/getprop/logcat\"}" > "$output/metadata.json"

run_capture() {
  local name="$1"
  shift
  "${adb[@]}" "$@" > "$output/$name.stdout.txt" 2> "$output/$name.stderr.txt" || true
}

run_capture adb_state get-state
run_capture fingerprint shell getprop ro.build.fingerprint
run_capture build_properties shell getprop
run_capture service_list shell service list
run_capture amazon_activity_manager shell dumpsys amazonactivitymanager
run_capture amazon_window_manager shell dumpsys amazonwindowmanager
run_capture amazon_user_manager shell dumpsys amazonusermanagerservice
run_capture amazon_profile_manager shell dumpsys amazonprofileservice
run_capture amazon_activity_package shell dumpsys package com.amazon.alexa.multimodal.gemini
run_capture firelauncher_package shell dumpsys package com.amazon.firelauncher
run_capture device_policy shell dumpsys device_policy
run_capture activity_top shell dumpsys activity top
run_capture home_resolution shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
run_capture preferred_xml shell dumpsys package preferred-xml
run_capture recent_logcat shell logcat -d -b system -v threadtime -t 300

if command -v shasum >/dev/null 2>&1; then
  (cd "$output" && shasum -a 256 *.json *.stdout.txt *.stderr.txt > sha256sums.txt)
else
  (cd "$output" && sha256sum *.json *.stdout.txt *.stderr.txt > sha256sums.txt)
fi
