#!/usr/bin/env bash
# Capture a complete Phase 3C state snapshot.
#
# This script is observational only. It never writes settings, package state,
# preferred activities, overlays, app-ops, or user data. Every command gets
# separate stdout, stderr, and exit-code files. The output directory must be
# new so that original evidence cannot be overwritten.

set -Eeuo pipefail

SERIAL=""
TEST_ID=""
OUTPUT=""
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  capture_phase3c_state.sh --serial SERIAL --test-id ID --output DIR [--dry-run]

The command requires an explicit ADB serial and refuses an existing output
directory. It performs read-only collection only.
EOF
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --test-id) [ "$#" -ge 2 ] || die '--test-id requires a value'; TEST_ID="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$OUTPUT" ] || die '--output is required'

ADB=(adb -s "$SERIAL")

commands=(
  "${ADB[*]} devices -l"
  "${ADB[*]} shell getprop"
  "${ADB[*]} shell id"
  "${ADB[*]} shell settings list system"
  "${ADB[*]} shell settings list secure"
  "${ADB[*]} shell settings list global"
  "${ADB[*]} shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0"
  "${ADB[*]} shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0"
  "${ADB[*]} shell pm query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0"
  "${ADB[*]} shell cmd package get-home-activities --user 0"
  "${ADB[*]} shell dumpsys package preferred-activities"
  "${ADB[*]} shell dumpsys package preferred-xml"
  "${ADB[*]} shell dumpsys package persistent-preferred-activities"
  "${ADB[*]} shell dumpsys package"
  "${ADB[*]} shell dumpsys package com.amazon.firelauncher"
  "${ADB[*]} shell pm path com.amazon.firelauncher"
  "${ADB[*]} shell pm list packages -f"
  "${ADB[*]} shell pm list packages -s"
  "${ADB[*]} shell pm list users"
  "${ADB[*]} shell cmd user list"
  "${ADB[*]} shell dumpsys user"
  "${ADB[*]} shell dumpsys activity activities"
  "${ADB[*]} shell dumpsys activity recents"
  "${ADB[*]} shell dumpsys activity top"
  "${ADB[*]} shell dumpsys window windows"
  "${ADB[*]} shell dumpsys input"
  "${ADB[*]} shell dumpsys role"
  "${ADB[*]} shell cmd role holders android.app.role.HOME --user 0"
  "${ADB[*]} shell dumpsys device_policy"
  "${ADB[*]} shell cmd overlay list"
  "${ADB[*]} shell dumpsys overlay"
  "${ADB[*]} shell device_config list"
  "${ADB[*]} shell dumpsys appops"
  "${ADB[*]} shell appops get com.amazon.firelauncher"
  "${ADB[*]} shell appops get com.microsoft.launcher"
  "${ADB[*]} shell appops get org.fireosresearch.home.p0"
  "${ADB[*]} shell ps -A -o USER,PID,PPID,NAME,ARGS"
  "${ADB[*]} shell cat /data/system/users/0/package-restrictions.xml"
  "${ADB[*]} shell cat /data/system/packages.xml"
  "${ADB[*]} shell cat /data/system/packages.list"
  "${ADB[*]} shell cat /data/system/users/0/runtime-permissions.xml"
)

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no ADB command will execute.\n'
  printf 'DRY-RUN: output=%s test-id=%s serial=%s\n' "$OUTPUT" "$TEST_ID" "$SERIAL"
  printf 'DRY-RUN: planned read-only commands:\n'
  printf '  %s\n' "${commands[@]}"
  exit 0
fi

case "$OUTPUT" in
  /|.|..|"") die "refusing unsafe output directory: $OUTPUT" ;;
esac
[ ! -e "$OUTPUT" ] || die "output directory already exists; refusing to overwrite: $OUTPUT"
mkdir -p "$OUTPUT/commands" "$OUTPUT/properties" "$OUTPUT/settings" "$OUTPUT/package" "$OUTPUT/activity" \
  "$OUTPUT/window" "$OUTPUT/security" "$OUTPUT/users" "$OUTPUT/overlay" "$OUTPUT/appops" "$OUTPUT/config"

printf 'test_id=%s\nserial=%s\ntimestamp_utc=%s\n' \
  "$TEST_ID" "$SERIAL" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.tsv"
printf '%s\n' "${commands[@]}" > "$OUTPUT/commands.txt"

run_capture() {
  local label="$1"
  shift
  local base="$OUTPUT/$label"
  mkdir -p "$(dirname "$base")"
  {
    printf 'command: '
    printf '%q ' "$@"
    printf '\n'
  } > "$base.command.txt"
  set +e
  "$@" > "$base.stdout.txt" 2> "$base.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$base.exit_code.txt"
}

run_capture devices "${ADB[@]}" devices -l
if ! awk -v serial="$SERIAL" '$1 == serial && $2 == "device" { found=1 } END { exit(found ? 0 : 1) }' \
    "$OUTPUT/devices.stdout.txt"; then
  die "serial is not connected in device state; see $OUTPUT/devices.stdout.txt"
fi

run_capture properties/getprop "${ADB[@]}" shell getprop
run_capture security/id "${ADB[@]}" shell id
run_capture security/selinux "${ADB[@]}" shell getenforce
run_capture security/uname "${ADB[@]}" shell uname -a

run_capture settings/system "${ADB[@]}" shell settings list system
run_capture settings/secure "${ADB[@]}" shell settings list secure
run_capture settings/global "${ADB[@]}" shell settings list global

run_capture package/home_resolve "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_capture package/home_query_cmd "${ADB[@]}" shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_capture package/home_query_pm "${ADB[@]}" shell pm query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_capture package/home_activities "${ADB[@]}" shell cmd package get-home-activities --user 0
run_capture package/preferred_activities "${ADB[@]}" shell dumpsys package preferred-activities
run_capture package/preferred_xml "${ADB[@]}" shell dumpsys package preferred-xml
run_capture package/persistent_preferred "${ADB[@]}" shell dumpsys package persistent-preferred-activities
run_capture package/full_dump "${ADB[@]}" shell dumpsys package
run_capture package/firelauncher "${ADB[@]}" shell dumpsys package com.amazon.firelauncher
run_capture package/firelauncher_path "${ADB[@]}" shell pm path com.amazon.firelauncher
run_capture package/all_packages "${ADB[@]}" shell pm list packages -f
run_capture package/system_packages "${ADB[@]}" shell pm list packages -s

run_capture users/pm_list_users "${ADB[@]}" shell pm list users
run_capture users/cmd_user_list "${ADB[@]}" shell cmd user list
run_capture users/dumpsys_user "${ADB[@]}" shell dumpsys user

run_capture activity/activities "${ADB[@]}" shell dumpsys activity activities
run_capture activity/recents "${ADB[@]}" shell dumpsys activity recents
run_capture activity/top "${ADB[@]}" shell dumpsys activity top
run_capture window/windows "${ADB[@]}" shell dumpsys window windows
run_capture window/input "${ADB[@]}" shell dumpsys input
run_capture window/processes "${ADB[@]}" shell ps -A -o USER,PID,PPID,NAME,ARGS

run_capture config/role_dump "${ADB[@]}" shell dumpsys role
run_capture config/home_role_holders "${ADB[@]}" shell cmd role holders android.app.role.HOME --user 0
run_capture config/device_policy "${ADB[@]}" shell dumpsys device_policy
run_capture config/device_config "${ADB[@]}" shell device_config list
run_capture overlay/list "${ADB[@]}" shell cmd overlay list
run_capture overlay/dump "${ADB[@]}" shell dumpsys overlay

run_capture appops/all "${ADB[@]}" shell dumpsys appops
run_capture appops/firelauncher "${ADB[@]}" shell appops get com.amazon.firelauncher
run_capture appops/microsoft "${ADB[@]}" shell appops get com.microsoft.launcher
run_capture appops/test_p0 "${ADB[@]}" shell appops get org.fireosresearch.home.p0

run_capture config/package_restrictions "${ADB[@]}" shell cat /data/system/users/0/package-restrictions.xml
run_capture config/packages_xml "${ADB[@]}" shell cat /data/system/packages.xml
run_capture config/packages_list "${ADB[@]}" shell cat /data/system/packages.list
run_capture config/runtime_permissions "${ADB[@]}" shell cat /data/system/users/0/runtime-permissions.xml

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
{
  printf '# Phase 3C state snapshot\n\n'
  printf '%s\n' "- Test ID: $TEST_ID"
  printf '%s\n' "- Serial: $SERIAL"
  printf '%s\n' "- Timestamp UTC: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  printf '%s\n' '- This snapshot executed read-only ADB commands only.'
  printf '%s\n' '- Individual command failures are preserved in *.exit_code.txt and are not silently treated as absence.'
  printf '%s\n' '- SHA-256 manifest: sha256sums.txt'
} > "$OUTPUT/summary.md"

printf 'Captured Phase 3C state snapshot in %s\n' "$OUTPUT"
