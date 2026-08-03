#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
RUN_ID=''
OUTPUT=''
WAIT_SECONDS='120'
APPROVE_STATE_CHANGE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: reboot_verify.sh --serial SERIAL --run-id ID --output DIR
       [--wait-seconds SECONDS] [--approve-state-change] [--dry-run]

Captures HOME/package/activity state, reboots the specified device, waits for
the same ADB serial to return, then captures the same state again. It does not
reset, flash, sideload, clear data, or alter settings. Live execution requires
an interactive approval phrase.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial)
      [ "$#" -ge 2 ] || die '--serial requires a value'
      SERIAL="$2"
      shift 2
      ;;
    --run-id)
      [ "$#" -ge 2 ] || die '--run-id requires a value'
      RUN_ID="$2"
      shift 2
      ;;
    --output)
      [ "$#" -ge 2 ] || die '--output requires a path'
      OUTPUT="$2"
      shift 2
      ;;
    --wait-seconds)
      [ "$#" -ge 2 ] || die '--wait-seconds requires a value'
      WAIT_SECONDS="$2"
      shift 2
      ;;
    --approve-state-change) APPROVE_STATE_CHANGE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$RUN_ID" ] || die '--run-id is required'
[ -n "$OUTPUT" ] || die '--output is required'
printf '%s' "$WAIT_SECONDS" | grep -Eq '^[1-9][0-9]*$' || die '--wait-seconds must be a positive integer'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: serial=%s run-id=%s wait-seconds=%s output=%s\n' "$SERIAL" "$RUN_ID" "$WAIT_SECONDS" "$OUTPUT"
  printf "DRY-RUN: read-only pre/post snapshots: adb -s '%s' shell cmd package resolve-activity ...\n" "$SERIAL"
  printf "DRY-RUN: gated command: adb -s '%s' reboot\n" "$SERIAL"
  printf 'DRY-RUN: post-reboot polling is bounded by %s seconds.\n' "$WAIT_SECONDS"
  exit 0
fi

validate_serial "$SERIAL"
ensure_new_path "$OUTPUT"
mkdir -p "$OUTPUT"
MANIFEST="$OUTPUT/command_manifest.tsv"
printf 'label\tstatus\tstarted_utc\tfinished_utc\tcommand\toutput\n' > "$MANIFEST"
HARD_FAILURES=0
LAST_STATUS=0
ADB_SERIAL="$SERIAL"

if [ "$APPROVE_STATE_CHANGE" -ne 1 ]; then
  die 'live reboot verification requires --approve-state-change and the interactive approval phrase'
fi
printf 'This test reboots the specified device and waits for the same ADB serial to return.\n'
printf 'Type APPROVE REBOOT %s to continue: ' "$RUN_ID"
read -r approval
[ "$approval" = "APPROVE REBOOT $RUN_ID" ] || die 'approval phrase did not match; no reboot command was executed'

capture_state() {
  local prefix="$1"
  run_adb_capture "${prefix}_getprop" no "$OUTPUT/${prefix}_getprop.txt" shell getprop
  run_adb_capture "${prefix}_home_resolve" no "$OUTPUT/${prefix}_home_resolve.txt" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
  run_adb_capture "${prefix}_home_query" no "$OUTPUT/${prefix}_home_query.txt" shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME
  run_adb_capture "${prefix}_package_firelauncher" no "$OUTPUT/${prefix}_package_firelauncher.txt" shell dumpsys package com.amazon.firelauncher
  run_adb_capture "${prefix}_activity" no "$OUTPUT/${prefix}_activity.txt" shell dumpsys activity activities
  run_adb_capture "${prefix}_window" no "$OUTPUT/${prefix}_window.txt" shell dumpsys window windows
}

printf 'run_id=%s\nserial=%s\nwait_seconds=%s\nstarted_utc=%s\n' \
  "$RUN_ID" "$SERIAL" "$WAIT_SECONDS" "$(timestamp_utc)" > "$OUTPUT/run_metadata.txt"
capture_state before

run_adb_capture 'reboot' yes "$OUTPUT/reboot.txt" reboot
reboot_status="$LAST_STATUS"
printf 'reboot_status=%s\nreboot_issued_utc=%s\n' "$reboot_status" "$(timestamp_utc)" >> "$OUTPUT/run_metadata.txt"

poll_file="$OUTPUT/reconnect_poll.tsv"
printf 'elapsed_seconds\tutc\tget_state\n' > "$poll_file"
reconnected=0
start_epoch=$(date +%s)
while :; do
  now_epoch=$(date +%s)
  elapsed=$((now_epoch - start_epoch))
  state=$(adb -s "$SERIAL" get-state 2>&1 || true)
  printf '%s\t%s\t%s\n' "$elapsed" "$(timestamp_utc)" "$state" >> "$poll_file"
  if [ "$state" = 'device' ]; then
    reconnected=1
    break
  fi
  if [ "$elapsed" -ge "$WAIT_SECONDS" ]; then
    break
  fi
  sleep 2
done
printf 'reconnected=%s\nreconnect_checked_utc=%s\n' "$reconnected" "$(timestamp_utc)" >> "$OUTPUT/run_metadata.txt"

if [ "$reconnected" -eq 1 ]; then
  readiness_file="$OUTPUT/package_service_poll.tsv"
  printf 'elapsed_seconds\tutc\tresolve_output\n' > "$readiness_file"
  package_ready=0
  readiness_start=$(date +%s)
  while :; do
    readiness_now=$(date +%s)
    readiness_elapsed=$((readiness_now - readiness_start))
    readiness_result=$(adb -s "$SERIAL" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME 2>&1 || true)
    printf '%s\t%s\t%s\n' "$readiness_elapsed" "$(timestamp_utc)" "$readiness_result" >> "$readiness_file"
    if printf '%s\n' "$readiness_result" | grep -q 'com.amazon.firelauncher/.Launcher'; then
      package_ready=1
      break
    fi
    if [ "$readiness_elapsed" -ge "$WAIT_SECONDS" ]; then
      break
    fi
    sleep 2
  done
  printf 'package_service_ready=%s\npackage_service_checked_utc=%s\n' "$package_ready" "$(timestamp_utc)" >> "$OUTPUT/run_metadata.txt"
  if [ "$package_ready" -eq 1 ]; then
    capture_state after
  else
    printf 'Post-reboot state capture skipped because the package service did not return within the bounded wait.\n' > "$OUTPUT/after_capture_skipped.txt"
    HARD_FAILURES=$((HARD_FAILURES + 1))
  fi
else
  printf 'Post-reboot state capture skipped because the device did not return within the bounded wait.\n' > "$OUTPUT/after_capture_skipped.txt"
  HARD_FAILURES=$((HARD_FAILURES + 1))
fi

if command -v rg >/dev/null 2>&1; then
  rg -n 'priority=|isDefault=|User [0-9]+:|enabled=|mResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|realActivity|origActivity|cmp=|ro.build|ro.boot.verifiedbootstate' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
else
  grep -REn 'priority=|isDefault=|User [0-9]+:|enabled=|mResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|realActivity|origActivity|cmp=|ro.build|ro.boot.verifiedbootstate' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
fi

{
  printf '# Reboot persistence verification summary\n\n'
  printf -- '- Run ID: `%s`\n' "$RUN_ID"
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- Reboot command exit status: `%s`\n' "$reboot_status"
  printf -- '- Reconnected within `%s` seconds: `%s`\n' "$WAIT_SECONDS" "$reconnected"
  printf -- '- Finding status: `Hypothesis` until before/after state and reconnect evidence are compared.\n\n'
  printf 'No factory reset, package clear, uninstall, flash, or sideload operation is performed by this script.\n'
} > "$OUTPUT/test_summary.md"

write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"
printf 'Reboot verification completed: %s\n' "$RUN_ID"
if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'Reboot verification completed with %s failure(s); inspect %s\n' "$HARD_FAILURES" "$MANIFEST" >&2
  exit 2
fi
