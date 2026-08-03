#!/usr/bin/env bash

# Phase 3B read-only baseline.  This script never changes package state,
# settings, preferred activities, foreground state, or boot state.

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
RUN_ID=''
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: collect_phase3b_baseline.sh --serial SERIAL [--run-id ID] [--dry-run]

Creates a new device/baseline/<ID> and adb/phase3b/<ID> directory.  Existing
paths are never overwritten.  Every ADB command is read-only and stdout,
stderr, exit status, command text, and SHA-256 values are retained.
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
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
if [ -z "$RUN_ID" ]; then
  RUN_ID="PHASE3B-BASELINE-$(timestamp_id)"
else
  RUN_ID=$(sanitize_id "$RUN_ID")
fi

DEVICE_DIR="$PROJECT_ROOT/device/baseline/$RUN_ID"
EVIDENCE_DIR="$PROJECT_ROOT/adb/phase3b/$RUN_ID"

command_plan() {
  cat <<EOF
Read-only Phase 3B commands for serial $SERIAL:
  getprop and selected build/security/classpath properties
  pm list packages -f/-s/-3/-d/-e; pm path for Fire/SystemUI/Settings/Amazon targets
  dumpsys package com.amazon.firelauncher
  dumpsys package preferred-activities/preferred-xml/persistent-preferred-activities
  cmd package and pm resolve/query HOME activities
  dumpsys activity activities/recents; dumpsys window windows
  dumpsys device_policy; cmd overlay list; cmd role get-role-holders HOME
  service list; dumpsys -l; ps -A; mount; /proc/mounts; getenforce; id; uname
  settings list secure/global/system; device_config list; appops get
EOF
}

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no ADB command or output directory will be created.\n'
  printf 'DRY-RUN: device output: %s\nDRY-RUN: evidence output: %s\n' "$DEVICE_DIR" "$EVIDENCE_DIR"
  command_plan
  exit 0
fi

validate_serial "$SERIAL"
require_command find
ensure_new_path "$DEVICE_DIR"
ensure_new_path "$EVIDENCE_DIR"
mkdir -p "$DEVICE_DIR/properties" "$DEVICE_DIR/packages" "$EVIDENCE_DIR/commands"

MANIFEST="$EVIDENCE_DIR/command_manifest.tsv"
printf 'label\tstatus\tstarted_utc\tfinished_utc\tcommand\tstdout\tstderr\n' > "$MANIFEST"
HARD_FAILURES=0
ADB_SERIAL="$SERIAL"

run_capture() {
  local label="$1"
  local required="$2"
  local base="$3"
  shift 3
  local started finished status command_text
  started=$(timestamp_utc)
  command_text="adb -s $(quote_arg "$SERIAL") $(render_command "$@")"
  set +e
  adb -s "$SERIAL" "$@" >"$base.stdout.txt" 2>"$base.stderr.txt"
  status=$?
  set -e
  finished=$(timestamp_utc)
  printf '%s\n' "$status" > "$base.exit_code.txt"
  if [ "$status" -ne 0 ] && [ "$required" = yes ]; then
    HARD_FAILURES=$((HARD_FAILURES + 1))
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$label" "$status" "$started" "$finished" "$command_text" \
    "$base.stdout.txt" "$base.stderr.txt" >> "$MANIFEST"
}

run_prop() {
  local key="$1"
  local safe=${key//./_}
  run_capture "getprop_$safe" yes "$DEVICE_DIR/properties/$safe" shell getprop "$key"
}

run_capture device_get_state yes "$DEVICE_DIR/get_state" get-state
run_capture devices yes "$DEVICE_DIR/devices" devices -l
run_capture getprop_all yes "$DEVICE_DIR/device_properties" shell getprop

for key in \
  ro.product.model ro.product.device ro.product.name ro.product.board \
  ro.hardware ro.boot.hardware ro.build.version.release ro.build.version.sdk \
  ro.build.version.incremental ro.build.version.security_patch \
  ro.build.fingerprint ro.build.type ro.build.tags ro.debuggable ro.secure \
  ro.adb.secure ro.boot.verifiedbootstate ro.boot.flash.locked \
  ro.boot.vbmeta.device_state ro.build.mktg.fireos ro.build.version.fireos \
  BOOTCLASSPATH SYSTEMSERVERCLASSPATH DEX2OATBOOTCLASSPATH; do
  run_prop "$key"
done

run_capture package_list yes "$DEVICE_DIR/package_list" shell pm list packages -f
run_capture system_packages yes "$DEVICE_DIR/system_packages" shell pm list packages -s
run_capture user_packages yes "$DEVICE_DIR/user_packages" shell pm list packages -3
run_capture disabled_packages yes "$DEVICE_DIR/disabled_packages" shell pm list packages -d
run_capture enabled_packages yes "$DEVICE_DIR/enabled_packages" shell pm list packages -e
run_capture package_users no "$DEVICE_DIR/package_users" shell pm list users
run_capture pm_help no "$DEVICE_DIR/pm_help" shell pm help
run_capture cmd_package_help no "$DEVICE_DIR/cmd_package_help" shell cmd package help

awk 'BEGIN{IGNORECASE=1} /amazon|launcher|home|settings|systemui|device|policy|parental|profile|kiosk|resolver|chooser|ota/ {print}' \
  "$DEVICE_DIR/package_list.stdout.txt" > "$DEVICE_DIR/packages/amazon_home_package_focus.txt" || true

for pkg in \
  com.amazon.firelauncher com.android.systemui com.android.settings \
  com.android.providers.settings com.amazon.settings com.amazon.parentalcontrols \
  com.amazon.device.messaging com.amazon.device.software.ota; do
  safe=$(sanitize_id "$pkg")
  run_capture "pm_path_$safe" no "$EVIDENCE_DIR/commands/pm_path_$safe" shell pm path "$pkg"
  run_capture "package_dump_$safe" no "$EVIDENCE_DIR/commands/package_dump_$safe" shell dumpsys package "$pkg"
done

run_capture package_dump_full yes "$EVIDENCE_DIR/commands/dumpsys_package_full" shell dumpsys package
run_capture preferred_activities no "$EVIDENCE_DIR/commands/preferred_activities" shell dumpsys package preferred-activities
run_capture preferred_xml no "$EVIDENCE_DIR/commands/preferred_xml" shell dumpsys package preferred-xml
run_capture persistent_preferred no "$EVIDENCE_DIR/commands/persistent_preferred" shell dumpsys package persistent-preferred-activities

run_capture home_resolve_cmd no "$EVIDENCE_DIR/commands/home_resolve_cmd" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_capture home_resolve_pm no "$EVIDENCE_DIR/commands/home_resolve_pm" shell pm resolve-activity -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_capture home_query_cmd no "$EVIDENCE_DIR/commands/home_query_cmd" shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_capture home_query_pm no "$EVIDENCE_DIR/commands/home_query_pm" shell pm query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0

run_capture activity_activities no "$EVIDENCE_DIR/commands/dumpsys_activity_activities" shell dumpsys activity activities
run_capture activity_recents no "$EVIDENCE_DIR/commands/dumpsys_activity_recents" shell dumpsys activity recents
run_capture window_windows no "$EVIDENCE_DIR/commands/dumpsys_window_windows" shell dumpsys window windows
run_capture input_state no "$EVIDENCE_DIR/commands/dumpsys_input" shell dumpsys input
run_capture device_policy no "$EVIDENCE_DIR/commands/dumpsys_device_policy" shell dumpsys device_policy
run_capture service_list yes "$DEVICE_DIR/service_list" shell service list
run_capture dumpsys_services yes "$DEVICE_DIR/dumpsys_services" shell dumpsys -l
run_capture process_list yes "$DEVICE_DIR/process_list" shell ps -A -o USER,PID,PPID,NAME,ARGS
run_capture mount yes "$DEVICE_DIR/mount_info" shell mount
run_capture proc_mounts yes "$DEVICE_DIR/mount_proc" shell cat /proc/mounts
run_capture security_getenforce yes "$DEVICE_DIR/security_getenforce" shell getenforce
run_capture security_id yes "$DEVICE_DIR/security_id" shell id
run_capture security_proc_version yes "$DEVICE_DIR/security_proc_version" shell cat /proc/version
run_capture security_uname yes "$DEVICE_DIR/security_uname" shell uname -a
run_capture overlays no "$EVIDENCE_DIR/commands/overlay_list" shell cmd overlay list
run_capture home_role_holders no "$EVIDENCE_DIR/commands/home_role_holders" shell cmd role get-role-holders android.app.role.HOME --user 0
run_capture current_user no "$EVIDENCE_DIR/commands/current_user" shell am get-current-user
run_capture user_dump no "$EVIDENCE_DIR/commands/user_dump" shell dumpsys user
run_capture settings_secure no "$EVIDENCE_DIR/commands/settings_secure" shell settings list secure
run_capture settings_global no "$EVIDENCE_DIR/commands/settings_global" shell settings list global
run_capture settings_system no "$EVIDENCE_DIR/commands/settings_system" shell settings list system
run_capture device_config no "$EVIDENCE_DIR/commands/device_config" shell device_config list
run_capture firelauncher_appops no "$EVIDENCE_DIR/commands/firelauncher_appops" shell appops get com.amazon.firelauncher

awk 'BEGIN{IGNORECASE=1} /amazon|launcher|home|settings|systemui|device|policy|parental|profile|kiosk|resolver|chooser|ota/ {print}' \
  "$DEVICE_DIR/service_list.stdout.txt" > "$DEVICE_DIR/packages/service_focus.txt" || true
awk 'BEGIN{IGNORECASE=1} /amazon|launcher|home|settings|systemui|device|policy|parental|profile|kiosk|resolver|chooser|ota|system_server/ {print}' \
  "$DEVICE_DIR/process_list.stdout.txt" > "$DEVICE_DIR/packages/process_focus.txt" || true

{
  printf 'field\tvalue\n'
  printf 'phase\t3B\n'
  printf 'serial\t%s\n' "$SERIAL"
  printf 'run_id\t%s\n' "$RUN_ID"
  printf 'collected_utc\t%s\n' "$(timestamp_utc)"
  printf 'device_output\t%s\n' "${DEVICE_DIR#$PROJECT_ROOT/}"
  printf 'evidence_output\t%s\n' "${EVIDENCE_DIR#$PROJECT_ROOT/}"
  printf 'state_changes\t0\nfire_launcher_mutation\t0\nlevel3_operations\t0\n'
} > "$EVIDENCE_DIR/metadata.tsv"

{
  printf '# Phase 3B read-only baseline\n\n'
  printf -- '- Run ID: `%s`\n' "$RUN_ID"
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- State-changing commands: `0`\n'
  printf -- '- Fire Launcher disable/clear/write: `0`\n'
  printf -- '- Level 3 operations: `0`\n'
  printf -- '- Required-command failures: `%s`\n\n' "$HARD_FAILURES"
  printf 'All command results are retained as separate stdout/stderr/exit-code files.\n'
  printf 'The command manifest records the exact ADB invocation and timestamps. This\n'
  printf 'summary intentionally does not infer the cause of HOME selection.\n'
} > "$EVIDENCE_DIR/summary.md"

write_sha256_manifest "$DEVICE_DIR" "$DEVICE_DIR/sha256sums.txt"
write_sha256_manifest "$EVIDENCE_DIR" "$EVIDENCE_DIR/sha256sums.txt"

if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'Phase 3B baseline completed with %s required failure(s): %s\n' "$HARD_FAILURES" "$RUN_ID" >&2
  exit 2
fi
printf 'Phase 3B baseline completed: %s\n' "$RUN_ID"
