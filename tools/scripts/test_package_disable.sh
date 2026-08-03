#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
PACKAGE=''
USER_ID='0'
OUTPUT=''
PACKAGE_TOOL='pm'
PACKAGE_COMMAND=(pm)
APPROVE_STATE_CHANGE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: test_package_disable.sh --serial SERIAL --package PACKAGE --output DIR
       [--user USER_ID] [--command pm|cmd] [--approve-state-change] [--dry-run]

Runs a bounded disable-user experiment and restores the package to Android's
default state afterward. It records the command result and before/after package
state; it does not reboot, clear data, uninstall, suspend, or change settings.
Live execution requires an interactive approval phrase.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial)
      [ "$#" -ge 2 ] || die '--serial requires a value'
      SERIAL="$2"
      shift 2
      ;;
    --package)
      [ "$#" -ge 2 ] || die '--package requires a value'
      PACKAGE="$2"
      shift 2
      ;;
    --user)
      [ "$#" -ge 2 ] || die '--user requires a value'
      USER_ID="$2"
      shift 2
      ;;
    --output)
      [ "$#" -ge 2 ] || die '--output requires a path'
      OUTPUT="$2"
      shift 2
      ;;
    --command)
      [ "$#" -ge 2 ] || die '--command requires a value'
      PACKAGE_TOOL="$2"
      shift 2
      ;;
    --approve-state-change) APPROVE_STATE_CHANGE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$PACKAGE" ] || die '--package is required'
[ -n "$OUTPUT" ] || die '--output is required'
printf '%s' "$USER_ID" | grep -Eq '^[0-9]+$' || die '--user must be a numeric user ID'
case "$PACKAGE_TOOL" in
  pm) PACKAGE_COMMAND=(pm) ;;
  cmd) PACKAGE_COMMAND=(cmd package) ;;
  *) die '--command must be pm or cmd' ;;
esac

print_plan() {
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: serial=%s package=%s user=%s command=%s output=%s\n' "$SERIAL" "$PACKAGE" "$USER_ID" "${PACKAGE_COMMAND[*]}" "$OUTPUT"
  printf "DRY-RUN: read-only snapshots: adb -s '%s' shell dumpsys package '%s'\n" "$SERIAL" "$PACKAGE"
  printf "DRY-RUN: gated command: adb -s '%s' shell %s disable-user --user '%s' '%s'\n" "$SERIAL" "${PACKAGE_COMMAND[*]}" "$USER_ID" "$PACKAGE"
  printf "DRY-RUN: gated restore: adb -s '%s' shell %s default-state --user '%s' '%s'\n" "$SERIAL" "${PACKAGE_COMMAND[*]}" "$USER_ID" "$PACKAGE"
  printf 'DRY-RUN: before/after/final snapshots, summary and SHA-256 manifest would be written under %s\n' "$OUTPUT"
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

if [ "$APPROVE_STATE_CHANGE" -ne 1 ]; then
  die 'live package test requires --approve-state-change and the interactive approval phrase'
fi
printf 'This test changes the package enabled state temporarily, then attempts to restore Android default state.\n'
printf 'Type APPROVE DISABLE %s to continue: ' "$PACKAGE"
read -r approval
[ "$approval" = "APPROVE DISABLE $PACKAGE" ] || die 'approval phrase did not match; no state-changing command was executed'

capture_state() {
  local phase="$1"
  run_adb_capture "${phase}_package" no "$OUTPUT/${phase}_package.txt" shell dumpsys package "$PACKAGE"
  run_adb_capture "${phase}_disabled_packages" no "$OUTPUT/${phase}_disabled_packages.txt" shell pm list packages -d
  run_adb_capture "${phase}_home_resolve" no "$OUTPUT/${phase}_home_resolve.txt" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user "$USER_ID"
  run_adb_capture "${phase}_activity" no "$OUTPUT/${phase}_activity.txt" shell dumpsys activity activities
  run_adb_capture "${phase}_window" no "$OUTPUT/${phase}_window.txt" shell dumpsys window windows
}

printf 'test_id=PACKAGE-DISABLE-%s\nserial=%s\npackage=%s\nuser=%s\ncommand=%s\nstarted_utc=%s\n' \
  "$(timestamp_id)" "$SERIAL" "$PACKAGE" "$USER_ID" "${PACKAGE_COMMAND[*]}" "$(timestamp_utc)" > "$OUTPUT/test_metadata.txt"

capture_state before

run_adb_capture 'disable_user' yes "$OUTPUT/disable_user.txt" shell "${PACKAGE_COMMAND[@]}" disable-user --user "$USER_ID" "$PACKAGE"
disable_status="$LAST_STATUS"
printf 'disable_status=%s\n' "$disable_status" >> "$OUTPUT/test_metadata.txt"

capture_state after_disable

# Always attempt restoration, including when disable-user failed. The command
# restores PackageManager's default enabled-state policy; it is not a guess at
# the user's prior setting. The pre-test dump remains the authoritative record
# of the original state.
run_adb_capture 'restore_default_state' yes "$OUTPUT/restore_default_state.txt" shell "${PACKAGE_COMMAND[@]}" default-state --user "$USER_ID" "$PACKAGE"
restore_status="$LAST_STATUS"
printf 'restore_status=%s\n' "$restore_status" >> "$OUTPUT/test_metadata.txt"

capture_state final

if command -v rg >/dev/null 2>&1; then
  rg -n 'enabled=|User [0-9]+:|Package \[|mResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|com\.amazon\.firelauncher|com\.android\.launcher3' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
else
  grep -REn 'enabled=|User [0-9]+:|Package \[|mResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|com\.amazon\.firelauncher|com\.android\.launcher3' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
fi

{
  printf '# Package disable test summary\n\n'
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- Package: `%s`\n' "$PACKAGE"
  printf -- '- User: `%s`\n' "$USER_ID"
  printf -- '- `%s disable-user` exit status: `%s`\n' "${PACKAGE_COMMAND[*]}" "$disable_status"
  printf -- '- `%s default-state` restore exit status: `%s`\n' "${PACKAGE_COMMAND[*]}" "$restore_status"
  printf -- '- Causal finding: `Hypothesis` until the command output and state snapshots are reviewed.\n\n'
  printf '## Evidence\n\n'
  printf -- '- [Command manifest](command_manifest.tsv)\n'
  printf -- '- [State focus lines](state_focus_lines.txt)\n'
  printf -- '- [SHA-256 manifest](sha256sums.txt)\n\n'
  printf 'The final snapshot must be compared with the pre-test snapshot before reporting restoration as successful.\n'
} > "$OUTPUT/test_summary.md"

write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"
printf 'Package disable test completed: %s\n' "$PACKAGE"
if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'Package disable test completed with %s command failure(s); inspect %s\n' "$HARD_FAILURES" "$MANIFEST" >&2
  exit 2
fi
