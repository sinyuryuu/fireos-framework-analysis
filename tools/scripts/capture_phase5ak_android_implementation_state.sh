#!/usr/bin/env bash
set -Eeuo pipefail

SERIAL=""
OUTPUT=""
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  capture_phase5ak_android_implementation_state.sh \
    --serial SERIAL --output OUTPUT [--dry-run]

This script performs read-only ADB collection for the Android redirect
implementation review. It never enables Accessibility, writes Settings,
changes package state, starts an APK, reboots, or touches Fire Launcher.
EOF
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial)
      [ "$#" -ge 2 ] || die '--serial requires a value'
      SERIAL="$2"
      shift 2
      ;;
    --output)
      [ "$#" -ge 2 ] || die '--output requires a value'
      OUTPUT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$OUTPUT" ] || die '--output is required'
[ "$OUTPUT" != "/" ] && [ "$OUTPUT" != "." ] && [ "$OUTPUT" != ".." ] || die 'unsafe output path'

ADB=(adb -s "$SERIAL")

if [ "$DRY_RUN" -eq 1 ]; then
  cat <<EOF
DRY-RUN: ${ADB[*]} get-state
DRY-RUN: ${ADB[*]} shell getprop
DRY-RUN: ${ADB[*]} shell settings get secure enabled_accessibility_services
DRY-RUN: ${ADB[*]} shell dumpsys accessibility
DRY-RUN: ${ADB[*]} shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
DRY-RUN: ${ADB[*]} shell pm path <research and Fire Launcher packages>
DRY-RUN: ${ADB[*]} shell dumpsys package <research and Fire Launcher packages>
DRY-RUN: ${ADB[*]} shell dumpsys activity activities
DRY-RUN: ${ADB[*]} shell dumpsys window windows
DRY-RUN: ${ADB[*]} shell cmd overlay list
DRY-RUN: ${ADB[*]} shell dumpsys role
DRY-RUN: ${ADB[*]} shell dumpsys device_policy
EOF
  exit 0
fi

[ ! -e "$OUTPUT" ] || die "refusing to overwrite existing output: $OUTPUT"
mkdir -p "$OUTPUT"

run_capture() {
  local name="$1"
  shift
  printf '%s\n' "${ADB[*]} $*" > "$OUTPUT/$name.command.txt"
  set +e
  "${ADB[@]}" "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
}

run_host_capture() {
  local name="$1"
  shift
  printf '%s\n' "$*" > "$OUTPUT/$name.command.txt"
  set +e
  "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
}

run_capture devices get-state
run_capture id shell id
run_capture getprop shell getprop
run_capture uname shell uname -a
run_capture accessibility_setting shell settings get secure enabled_accessibility_services
run_capture accessibility_dump shell dumpsys accessibility
run_capture home_resolver shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_capture home_query shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_capture firelauncher_path shell pm path com.amazon.firelauncher
run_capture redirect_path shell pm path org.fireosresearch.phase4.redirect
run_capture alias_path shell pm path org.fireosresearch.phase4.alias
run_capture firelauncher_package shell dumpsys package com.amazon.firelauncher
run_capture redirect_package shell dumpsys package org.fireosresearch.phase4.redirect
run_capture alias_package shell dumpsys package org.fireosresearch.phase4.alias
run_capture activity_activities shell dumpsys activity activities
run_capture activity_top shell dumpsys activity top
run_capture window_windows shell dumpsys window windows
run_capture overlay_list shell cmd overlay list
run_capture role_dump shell dumpsys role
run_capture device_policy shell dumpsys device_policy
run_capture users shell pm list users
run_capture appops_redirect shell appops get org.fireosresearch.phase4.redirect
run_capture appops_alias shell appops get org.fireosresearch.phase4.alias
run_capture appops_firelauncher shell appops get com.amazon.firelauncher

timestamp_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
cat > "$OUTPUT/metadata.tsv" <<EOF
test_id\tPHASE5AK-ANDROID-IMPLEMENTATION-STATE
serial\t$SERIAL
timestamp_utc\t$timestamp_utc
scope\tread-only Android implementation state capture
mutations\tNONE
accessibility_enable\tNOT_EXECUTED
firelauncher_mutation\tNOT_EXECUTED
reboot\tNOT_EXECUTED
EOF

run_host_capture host_tool_versions sh -c 'printf "date\t"; date -u; printf "adb\t"; adb version | head -1; printf "shasum\t"; shasum --version | head -1'
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Read-only Phase 5AK state captured in %s\n' "$OUTPUT"
