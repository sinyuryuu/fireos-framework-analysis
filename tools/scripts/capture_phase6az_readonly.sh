#!/usr/bin/env bash
set -euo pipefail

# Phase 6AZ: explicit-serial, read-only PS7331 runtime capture.
# This script intentionally contains no package/settings mutation, Binder
# transaction, broadcast, reboot, install, force-stop, or partition command.

usage() {
  echo "usage: $0 --serial DEVICE_SERIAL --output OUTPUT_DIR" >&2
  exit 2
}

SERIAL=""
OUTPUT=""
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --serial)
      [[ $# -ge 2 ]] || usage
      SERIAL="$2"
      shift 2
      ;;
    --output)
      [[ $# -ge 2 ]] || usage
      OUTPUT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --help)
      usage
      ;;
    *) usage ;;
  esac
done

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "No device command would be executed. Required serial=${SERIAL:-<missing>} output=${OUTPUT:-<missing>}"
  exit 0
fi

[[ -n "$SERIAL" && -n "$OUTPUT" ]] || usage
command -v adb >/dev/null 2>&1 || { echo "adb not found" >&2; exit 1; }
[[ ! -e "$OUTPUT" ]] || { echo "refusing to overwrite existing output: $OUTPUT" >&2; exit 1; }

mkdir -p "$OUTPUT"
COMMANDS="$OUTPUT/commands.txt"
: > "$COMMANDS"

TEST_ID="${OUTPUT##*/}"
printf 'test_id=%s\nserial=%s\ntimestamp_utc=%s\n' \
  "$TEST_ID" "$SERIAL" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.txt"

capture() {
  local name="$1"
  shift
  printf '%s\n' "$(printf '%q ' "$@")" >> "$COMMANDS"
  set +e
  "$@" > "$OUTPUT/${name}.stdout.txt" 2> "$OUTPUT/${name}.stderr.txt"
  local status=$?
  set -e
  printf '%s=%s\n' "$name" "$status" >> "$OUTPUT/exit-codes.txt"
}

ADB=(adb -s "$SERIAL")

# Verify the explicitly selected device before collecting any other state.
capture get_state "${ADB[@]}" get-state

capture getprop "${ADB[@]}" shell getprop
capture security_state "${ADB[@]}" shell sh -c 'getenforce; id; uname -a'
capture home_resolve "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
capture home_candidates "${ADB[@]}" shell cmd package query-activities --brief -a android.intent.action.MAIN -c android.intent.category.HOME
capture firelauncher_package "${ADB[@]}" shell dumpsys package com.amazon.firelauncher
capture preferred_activities "${ADB[@]}" shell dumpsys package preferred-activities
capture activity_activities "${ADB[@]}" shell dumpsys activity activities
capture activity_recents "${ADB[@]}" shell dumpsys activity recents
capture window_windows "${ADB[@]}" shell dumpsys window windows
capture device_policy "${ADB[@]}" shell dumpsys device_policy
capture role "${ADB[@]}" shell dumpsys role
capture users "${ADB[@]}" shell pm list users
capture settings_system "${ADB[@]}" shell settings list system
capture settings_secure "${ADB[@]}" shell settings list secure
capture settings_global "${ADB[@]}" shell settings list global
capture device_config "${ADB[@]}" shell device_config list
capture firelauncher_appops "${ADB[@]}" shell appops get com.amazon.firelauncher
capture tb_custom_launcher_value "${ADB[@]}" shell settings get --user 0 secure tb_custom_launcher
capture enabled_accessibility_services_value "${ADB[@]}" shell settings get --user 0 secure enabled_accessibility_services
capture relevant_packages "${ADB[@]}" shell sh -c 'pm list packages -f | grep -iE "amazon|launcher|fireosresearch|teslacoilsw"'
capture teslacoilsw_package "${ADB[@]}" shell dumpsys package com.teslacoilsw.launcher
capture phase4_redirect_package "${ADB[@]}" shell dumpsys package org.fireosresearch.phase4.redirect
capture phase4_alias_package "${ADB[@]}" shell dumpsys package org.fireosresearch.phase4.alias
capture overlays "${ADB[@]}" shell cmd overlay list
capture services "${ADB[@]}" shell service list

printf 'host_only=false\ndevice_contacted=true\nmutations_requested=false\n' >> "$OUTPUT/metadata.txt"
printf '# Phase 6AZ read-only capture\n\nSerial: `%s`\n\nNo mutation command is present in `commands.txt`.\n' "$SERIAL" > "$OUTPUT/result.md"

(cd "$OUTPUT" && shasum -a 256 -- * > sha256sums.txt)
echo "$OUTPUT"
