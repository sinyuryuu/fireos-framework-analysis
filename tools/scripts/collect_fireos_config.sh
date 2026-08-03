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
Usage: collect_fireos_config.sh --serial SERIAL [--output-dir PROJECT_ROOT]
       [--run-id ID] [--dry-run]

Collects read-only Fire OS configuration paths, vendor callback XML listings,
PackageManager deny-list path metadata, and system_server code mappings.
It never writes to the device.
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

OUTPUT_ROOT="$OUTPUT_DIR/device/fireos-config/$RUN_ID"

readonly_command_plan() {
  cat <<EOF
Read-only commands for serial $SERIAL:
  adb -s '$SERIAL' get-state
  adb -s '$SERIAL' shell getprop
  adb -s '$SERIAL' shell ls -ld <Fire OS directory candidates>
  adb -s '$SERIAL' shell find <Fire OS directory candidates> -type f -name '*.xml'
  adb -s '$SERIAL' shell ls -la <PackageManager deny-list candidates>
  adb -s '$SERIAL' shell find /data/system /data/system_de -iname '*Deny*'
  adb -s '$SERIAL' shell pidof system_server
  adb -s '$SERIAL' shell cat /proc/<system_server-pid>/maps
EOF
}

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: output would be %s\n' "$OUTPUT_ROOT"
  readonly_command_plan
  exit 0
fi

validate_serial "$SERIAL"
require_command awk
require_command find
ensure_new_path "$OUTPUT_ROOT"
mkdir -p "$OUTPUT_ROOT/paths"

MANIFEST="$OUTPUT_ROOT/command_manifest.tsv"
printf 'label\tstatus\tstarted_utc\tfinished_utc\tcommand\toutput\n' > "$MANIFEST"
HARD_FAILURES=0
LAST_STATUS=0
ADB_SERIAL="$SERIAL"

run_adb_capture 'device_get_state' yes "$OUTPUT_ROOT/get_state.txt" get-state
run_adb_capture 'getprop_all' yes "$OUTPUT_ROOT/device_properties.txt" shell getprop

for path in /fireos /system/fireos /product/fireos /system_ext/fireos /vendor/fireos \
  /fireos/etc /system/fireos/etc /product/fireos/etc /system_ext/fireos/etc \
  /fireos/etc/permissions /system/fireos/etc/permissions /product/fireos/etc/permissions /system_ext/fireos/etc/permissions \
  /fireos/etc/init /system/fireos/etc/init /product/fireos/etc/init /system_ext/fireos/etc/init \
  /system/etc/permissions /system/etc/init; do
  safe_path=$(sanitize_id "$path")
  run_adb_capture "ls_${safe_path}" no "$OUTPUT_ROOT/paths/ls_${safe_path}.txt" shell ls -ld "$path"
done

for path in /fireos/etc/permissions /system/fireos/etc/permissions /product/fireos/etc/permissions \
  /system_ext/fireos/etc/permissions /system/etc/permissions; do
  safe_path=$(sanitize_id "$path")
  run_adb_capture "find_xml_${safe_path}" no "$OUTPUT_ROOT/paths/find_xml_${safe_path}.txt" shell find "$path" -maxdepth 1 -type f -name '*.xml' -print
done

for path in /fireos/etc/init /system/fireos/etc/init /product/fireos/etc/init \
  /system_ext/fireos/etc/init /system/etc/init; do
  safe_path=$(sanitize_id "$path")
  run_adb_capture "find_init_xml_${safe_path}" no "$OUTPUT_ROOT/paths/find_init_xml_${safe_path}.txt" shell find "$path" -maxdepth 1 -type f -name '*.xml' -print
done

for path in /data/system/PackageManagerDenyList /data/system/PackageManagerDenyList.xml \
  /data/system_de/0/shared_prefs/PackageManagerDenyList \
  /data/system_de/0/shared_prefs/PackageManagerDenyList.xml \
  /data/system_de/0/shared_prefs; do
  safe_path=$(sanitize_id "$path")
  run_adb_capture "ls_deny_${safe_path}" no "$OUTPUT_ROOT/paths/ls_deny_${safe_path}.txt" shell ls -la "$path"
done
run_adb_capture 'find_deny_paths' no "$OUTPUT_ROOT/paths/find_deny_paths.txt" shell find /data/system /data/system_de -iname '*Deny*' -print

run_adb_capture 'system_server_pid' yes "$OUTPUT_ROOT/system_server_pid.txt" shell pidof system_server
SYSTEM_SERVER_PID=$(awk 'NF { print $1; exit }' "$OUTPUT_ROOT/system_server_pid.txt")
if [ -n "$SYSTEM_SERVER_PID" ]; then
  run_adb_capture 'system_server_maps' no "$OUTPUT_ROOT/system_server_maps.txt" shell cat "/proc/$SYSTEM_SERVER_PID/maps"
else
  printf 'system_server PID could not be parsed; maps not collected.\n' > "$OUTPUT_ROOT/system_server_maps.txt"
fi

{
  printf '# Fire OS configuration/runtime mapping collection\n\n'
  printf -- '- Run ID: `%s`\n' "$RUN_ID"
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- Collected at (UTC): `%s`\n' "$(timestamp_utc)"
  printf -- '- Hard command failures: `%s`\n' "$HARD_FAILURES"
  printf -- '- All observations remain raw until manually correlated with bytecode.\n\n'
  printf '## Intended configuration roots\n\n'
  printf -- 'The Fire OS bytecode calls `Environment.getFireOsDirectory()` and appends `/etc/permissions` and `/etc/init`; this run records candidate resolved paths without assuming the result.\n'
} > "$OUTPUT_ROOT/summary.md"

write_sha256_manifest "$OUTPUT_ROOT" "$OUTPUT_ROOT/sha256sums.txt"

if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'Fire OS config collection completed with %s required failure(s): %s\n' "$HARD_FAILURES" "$RUN_ID" >&2
  exit 2
fi
printf 'Fire OS config collection completed: %s\n' "$RUN_ID"
