#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
OUTPUT_DIR="$PROJECT_ROOT"
RUN_ID=''
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: collect_device_baseline.sh --serial SERIAL [--output-dir PROJECT_ROOT] [--run-id ID] [--dry-run]

Collects read-only device, package, service, security, resolver and state data.
No package state or device setting is changed.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial)
      [ "$#" -ge 2 ] || die '--serial requires a value'
      SERIAL="$2"
      shift 2
      ;;
    --output-dir)
      [ "$#" -ge 2 ] || die '--output-dir requires a path'
      OUTPUT_DIR="$2"
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
  RUN_ID="$(timestamp_id)_$(sanitize_id "$SERIAL")"
else
  RUN_ID=$(sanitize_id "$RUN_ID")
fi

DEVICE_ROOT="$OUTPUT_DIR/device/baseline/$RUN_ID"
ADB_ROOT="$OUTPUT_DIR/adb/baseline/$RUN_ID"

readonly_command_plan() {
  cat <<EOF
Read-only commands for serial $SERIAL:
  adb -s '$SERIAL' get-state
  adb -s '$SERIAL' shell getprop
  adb -s '$SERIAL' shell pm list packages -f|-s|-3|-d|-e
  adb -s '$SERIAL' shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
  adb -s '$SERIAL' shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME
  adb -s '$SERIAL' shell dumpsys package preferred-activities
  adb -s '$SERIAL' shell dumpsys package
  adb -s '$SERIAL' shell service list
  adb -s '$SERIAL' shell dumpsys -l
  adb -s '$SERIAL' shell ps -A -o USER,PID,PPID,NAME,ARGS
  adb -s '$SERIAL' shell mount
  adb -s '$SERIAL' shell cat /proc/mounts
  adb -s '$SERIAL' shell getenforce; id; cat /proc/version; uname -a
  adb -s '$SERIAL' shell cmd overlay list
  adb -s '$SERIAL' shell pm list users; am get-current-user; dumpsys user
  adb -s '$SERIAL' shell settings list secure|global|system
  adb -s '$SERIAL' shell device_config list

Hypotheses:
  identity/build: exact device and Fire OS build
  package state: system/privileged/persistent/enabled/protected candidates
  home resolver: standard HOME resolution versus custom selection
  service/process: Amazon ActivityManager/WindowManager/Input/PackageManager paths
  security: shell identity, SELinux and verified boot constraints
  overlay/settings: UI and resource-level default-home controls
EOF
}

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: output would be:\n  %s\n  %s\n' "$DEVICE_ROOT" "$ADB_ROOT"
  readonly_command_plan
  exit 0
fi

validate_serial "$SERIAL"
require_command awk
require_command find
ensure_new_path "$DEVICE_ROOT"
ensure_new_path "$ADB_ROOT"
mkdir -p "$DEVICE_ROOT/properties" "$DEVICE_ROOT/packages" "$ADB_ROOT"

MANIFEST="$ADB_ROOT/command_manifest.tsv"
printf 'label\tstatus\tstarted_utc\tfinished_utc\tcommand\toutput\n' > "$MANIFEST"
HARD_FAILURES=0
LAST_STATUS=0
ADB_SERIAL="$SERIAL"

run_adb_capture 'device_get_state' yes "$DEVICE_ROOT/get_state.txt" get-state
run_adb_capture 'getprop_all' yes "$DEVICE_ROOT/device_properties.txt" shell getprop

PROPERTY_KEYS='ro.product.model ro.product.device ro.product.name ro.product.board ro.hardware ro.boot.hardware ro.build.version.release ro.build.version.sdk ro.build.version.incremental ro.build.version.security_patch ro.build.fingerprint ro.build.type ro.build.tags ro.debuggable ro.secure ro.adb.secure ro.boot.verifiedbootstate ro.boot.flash.locked ro.boot.vbmeta.device_state ro.build.mktg.fireos ro.build.version.fireos'
for key in $PROPERTY_KEYS; do
  safe_key=${key//./_}
  run_adb_capture "getprop_$safe_key" yes "$DEVICE_ROOT/properties/$safe_key.txt" shell getprop "$key"
done

run_adb_capture 'packages_all' yes "$DEVICE_ROOT/package_list.txt" shell pm list packages -f
run_adb_capture 'packages_system' yes "$DEVICE_ROOT/system_packages.txt" shell pm list packages -s
run_adb_capture 'packages_user' yes "$DEVICE_ROOT/user_packages.txt" shell pm list packages -3
run_adb_capture 'packages_disabled' yes "$DEVICE_ROOT/disabled_packages.txt" shell pm list packages -d
run_adb_capture 'packages_enabled' yes "$DEVICE_ROOT/enabled_packages.txt" shell pm list packages -e
run_adb_capture 'packages_users' yes "$DEVICE_ROOT/packages/user_list.txt" shell pm list users
run_adb_capture 'pm_help' no "$DEVICE_ROOT/pm_help.txt" shell pm help
run_adb_capture 'cmd_package_help' no "$DEVICE_ROOT/cmd_package_help.txt" shell cmd package help
run_adb_capture 'cmd_activity_help' no "$DEVICE_ROOT/cmd_activity_help.txt" shell cmd activity help

awk '{ line=tolower($0); if (line ~ /amazon|launcher|home|settings|systemui/) print }' \
  "$DEVICE_ROOT/package_list.txt" > "$DEVICE_ROOT/packages/package_focus.txt" || true

run_adb_capture 'home_resolve_cmd' no "$ADB_ROOT/home_resolve_cmd.txt" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
if [ "$LAST_STATUS" -ne 0 ]; then
  run_adb_capture 'home_resolve_pm_fallback' yes "$ADB_ROOT/home_resolve_pm_fallback.txt" shell pm resolve-activity -a android.intent.action.MAIN -c android.intent.category.HOME
fi

run_adb_capture 'home_query_cmd' no "$ADB_ROOT/home_query_cmd.txt" shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME
if [ "$LAST_STATUS" -ne 0 ]; then
  run_adb_capture 'package_dump_full_fallback' yes "$ADB_ROOT/home_query_dumpsys_fallback.txt" shell dumpsys package
fi

run_adb_capture 'preferred_activities' no "$ADB_ROOT/preferred_activities.txt" shell dumpsys package preferred-activities
run_adb_capture 'package_dump_full' yes "$ADB_ROOT/dumpsys_package_full.txt" shell dumpsys package

candidate_file="$ADB_ROOT/home_candidates.txt"
{
  sed -n 's/.*packageName=\([^[:space:]]*\).*/\1/p' "$ADB_ROOT/home_query_cmd.txt" 2>/dev/null || true
  sed -n 's#^\([^/[:space:]]*\)/.*#\1#p' "$ADB_ROOT/home_resolve_cmd.txt" 2>/dev/null || true
  sed -n 's#^\([^/[:space:]]*\)/.*#\1#p' "$ADB_ROOT/home_resolve_pm_fallback.txt" 2>/dev/null || true
} | awk 'NF && !seen[$0]++' > "$candidate_file"

while IFS= read -r package_name; do
  [ -n "$package_name" ] || continue
  safe_package=$(sanitize_id "$package_name")
  run_adb_capture "package_dump_$safe_package" no "$ADB_ROOT/package_${safe_package}.txt" shell dumpsys package "$package_name"
  run_adb_capture "package_path_$safe_package" no "$ADB_ROOT/path_${safe_package}.txt" shell pm path "$package_name"
done < "$candidate_file"

run_adb_capture 'service_list' yes "$DEVICE_ROOT/service_list.txt" shell service list
run_adb_capture 'dumpsys_service_names' yes "$DEVICE_ROOT/dumpsys_services.txt" shell dumpsys -l
run_adb_capture 'process_list' yes "$DEVICE_ROOT/process_list.txt" shell ps -A -o USER,PID,PPID,NAME,ARGS
awk '{ line=tolower($0); if (line ~ /amazon|launcher|home|settings|systemui|activity|window|input|policy|ota/) print }' \
  "$DEVICE_ROOT/service_list.txt" > "$DEVICE_ROOT/packages/service_focus.txt" || true
awk '{ line=tolower($0); if (line ~ /amazon|launcher|home|settings|systemui|activity|window|input|policy|ota/) print }' \
  "$DEVICE_ROOT/process_list.txt" > "$DEVICE_ROOT/packages/process_focus.txt" || true

run_adb_capture 'mount' yes "$DEVICE_ROOT/mount_info.txt" shell mount
run_adb_capture 'proc_mounts' yes "$DEVICE_ROOT/mount_proc.txt" shell cat /proc/mounts
run_adb_capture 'getenforce' yes "$DEVICE_ROOT/security_getenforce.txt" shell getenforce
run_adb_capture 'identity' yes "$DEVICE_ROOT/security_id.txt" shell id
run_adb_capture 'proc_version' yes "$DEVICE_ROOT/security_proc_version.txt" shell cat /proc/version
run_adb_capture 'uname' yes "$DEVICE_ROOT/security_uname.txt" shell uname -a
run_adb_capture 'overlay_list' no "$DEVICE_ROOT/overlay_list.txt" shell cmd overlay list
run_adb_capture 'current_user' no "$DEVICE_ROOT/current_user.txt" shell am get-current-user
run_adb_capture 'user_dump' no "$DEVICE_ROOT/user_dump.txt" shell dumpsys user
run_adb_capture 'settings_secure_read' no "$DEVICE_ROOT/settings_secure.txt" shell settings list secure
run_adb_capture 'settings_global_read' no "$DEVICE_ROOT/settings_global.txt" shell settings list global
run_adb_capture 'settings_system_read' no "$DEVICE_ROOT/settings_system.txt" shell settings list system
run_adb_capture 'device_config_read' no "$DEVICE_ROOT/device_config.txt" shell device_config list

for dump in activities recents; do
  run_adb_capture "activity_$dump" no "$ADB_ROOT/dumpsys_activity_$dump.txt" shell dumpsys activity "$dump"
done
run_adb_capture 'window_windows' no "$ADB_ROOT/dumpsys_window_windows.txt" shell dumpsys window windows
run_adb_capture 'input' no "$ADB_ROOT/dumpsys_input.txt" shell dumpsys input

{
  printf '# Device baseline summary\n\n'
  printf -- '- Run ID: `%s`\n' "$RUN_ID"
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- Collected at (UTC): `%s`\n' "$(timestamp_utc)"
  printf -- '- Hard command failures: `%s`\n' "$HARD_FAILURES"
  printf -- '- Finding status: `Hypothesis` until raw evidence is manually reviewed.\n\n'
  printf '## HOME candidates discovered from command output\n\n'
  if [ -s "$candidate_file" ]; then
    while IFS= read -r package_name; do printf -- '- `%s`\n' "$package_name"; done < "$candidate_file"
  else
    printf -- '- None parsed automatically; inspect resolver and full package dumps.\n'
  fi
  printf '\n## Evidence files\n\n'
  printf -- '- [Command manifest](command_manifest.tsv)\n'
  printf -- '- [SHA-256 manifest](sha256sums.txt)\n'
  printf -- '- [HOME candidates](home_candidates.txt)\n'
  printf '\nThe script records observations and command results; it does not infer why Amazon selects a launcher.\n'
} > "$ADB_ROOT/summary.md"

write_sha256_manifest "$DEVICE_ROOT" "$DEVICE_ROOT/sha256sums.txt"
write_sha256_manifest "$ADB_ROOT" "$ADB_ROOT/sha256sums.txt"

if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'Baseline completed with %s required command failure(s): %s\n' "$HARD_FAILURES" "$RUN_ID" >&2
  exit 2
fi
printf 'Baseline completed: %s\n' "$RUN_ID"
