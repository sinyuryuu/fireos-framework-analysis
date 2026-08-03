#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
TEST_ID=''
OUTPUT=''
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: probe_device_policy.sh --serial SERIAL --test-id POLICY-TNN --output DIR
       [--dry-run]

Captures read-only DevicePolicy, UserManager and relevant package state. It
does not set or clear an owner/admin, change restrictions, modify settings,
change package state, reboot, or change the foreground activity.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial)
      [ "$#" -ge 2 ] || die '--serial requires a value'
      SERIAL="$2"
      shift 2
      ;;
    --test-id)
      [ "$#" -ge 2 ] || die '--test-id requires a value'
      TEST_ID="$2"
      shift 2
      ;;
    --output)
      [ "$#" -ge 2 ] || die '--output requires a path'
      OUTPUT="$2"
      shift 2
      ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$OUTPUT" ] || die '--output is required'
printf '%s' "$TEST_ID" | grep -Eq '^POLICY-T[0-9]{2,}$' || die '--test-id must match POLICY-TNN'

print_plan() {
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: serial=%s test-id=%s output=%s\n' "$SERIAL" "$TEST_ID" "$OUTPUT"
  printf 'DRY-RUN: read-only commands: dumpsys device_policy, dumpsys user, cmd device_policy help\n'
  printf 'DRY-RUN: read-only package dumps: com.amazon.parentalcontrols, com.google.android.gms, com.amazon.firelauncher\n'
  printf 'DRY-RUN: command manifest, summary and SHA-256 manifest would be written under %s\n' "$OUTPUT"
}

if [ "$DRY_RUN" -eq 1 ]; then
  print_plan
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

printf 'test_id=%s\nserial=%s\nstarted_utc=%s\n' \
  "$TEST_ID" "$SERIAL" "$(timestamp_utc)" > "$OUTPUT/test_metadata.txt"

run_adb_capture 'device_policy' no "$OUTPUT/device_policy.txt" shell dumpsys device_policy
run_adb_capture 'user' no "$OUTPUT/user.txt" shell dumpsys user
run_adb_capture 'device_policy_help' no "$OUTPUT/device_policy_help.txt" shell cmd device_policy help
run_adb_capture 'parentalcontrols_package' no "$OUTPUT/package_com.amazon.parentalcontrols.txt" shell dumpsys package com.amazon.parentalcontrols
run_adb_capture 'gms_package' no "$OUTPUT/package_com.google.android.gms.txt" shell dumpsys package com.google.android.gms
run_adb_capture 'firelauncher_package' no "$OUTPUT/package_com.amazon.firelauncher.txt" shell dumpsys package com.amazon.firelauncher
run_adb_capture 'service_list' no "$OUTPUT/service_list.txt" shell service list
run_adb_capture 'activity_state' no "$OUTPUT/activity_state.txt" shell dumpsys activity activities

if command -v rg >/dev/null 2>&1; then
  rg -n 'Profile Owner|Device Owner|Device managed|Has profile owner|User restrictions|com\.amazon\.parentalcontrols|com\.google\.android\.gms|com\.amazon\.firelauncher|HOME|home|launcher|restriction|admin' \
    "$OUTPUT" > "$OUTPUT/focus_lines.txt" || true
else
  grep -REn 'Profile Owner|Device Owner|Device managed|Has profile owner|User restrictions|com\.amazon\.parentalcontrols|com\.google\.android\.gms|com\.amazon\.firelauncher|HOME|home|launcher|restriction|admin' \
    "$OUTPUT" > "$OUTPUT/focus_lines.txt" || true
fi

printf 'finished_utc=%s\n' "$(timestamp_utc)" >> "$OUTPUT/test_metadata.txt"

{
  printf '# DevicePolicy read-only probe summary\n\n'
  printf -- '- Test ID: `%s`\n' "$TEST_ID"
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- State change: none; all commands are read-only.\n'
  printf -- '- Finding status: `Hypothesis` until the captured owner/admin and restriction state is reviewed.\n\n'
  printf '## Evidence\n\n'
  printf -- '- [DevicePolicy dump](device_policy.txt)\n'
  printf -- '- [User dump](user.txt)\n'
  printf -- '- [Relevant package dumps](package_com.amazon.parentalcontrols.txt)\n'
  printf -- '- [Focus lines](focus_lines.txt)\n'
  printf -- '- [Command manifest](command_manifest.tsv)\n'
  printf -- '- [SHA-256 manifest](sha256sums.txt)\n'
} > "$OUTPUT/test_summary.md"

write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"
printf 'DevicePolicy probe completed: %s\n' "$TEST_ID"
if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'DevicePolicy probe completed with %s required command failure(s); inspect %s\n' "$HARD_FAILURES" "$MANIFEST" >&2
  exit 2
fi
