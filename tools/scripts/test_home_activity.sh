#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
TARGET=''
RESTORE=''
USER_ID='0'
OUTPUT=''
TEST_ID=''
APPROVE_STATE_CHANGE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: test_home_activity.sh --serial SERIAL --test-id ID --target PACKAGE/ACTIVITY
       --restore PACKAGE/ACTIVITY --output DIR [--user USER_ID]
       [--approve-state-change] [--dry-run]

Runs cmd package set-home-activity for one target, records resolver and
foreground state, then attempts to restore the supplied component.
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
    --test-id)
      [ "$#" -ge 2 ] || die '--test-id requires a value'
      TEST_ID="$2"
      shift 2
      ;;
    --target)
      [ "$#" -ge 2 ] || die '--target requires a value'
      TARGET="$2"
      shift 2
      ;;
    --restore)
      [ "$#" -ge 2 ] || die '--restore requires a value'
      RESTORE="$2"
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
    --approve-state-change) APPROVE_STATE_CHANGE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$TARGET" ] || die '--target is required'
[ -n "$RESTORE" ] || die '--restore is required'
[ -n "$OUTPUT" ] || die '--output is required'
printf '%s' "$USER_ID" | grep -Eq '^[0-9]+$' || die '--user must be a numeric user ID'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: serial=%s test-id=%s user=%s target=%s restore=%s output=%s\n' \
    "$SERIAL" "$TEST_ID" "$USER_ID" "$TARGET" "$RESTORE" "$OUTPUT"
  printf "DRY-RUN: read-only snapshots: adb -s '%s' shell cmd package resolve-activity ...\n" "$SERIAL"
  printf "DRY-RUN: gated command: adb -s '%s' shell cmd package set-home-activity --user '%s' '%s'\n" "$SERIAL" "$USER_ID" "$TARGET"
  printf "DRY-RUN: gated restore: adb -s '%s' shell cmd package set-home-activity --user '%s' '%s'\n" "$SERIAL" "$USER_ID" "$RESTORE"
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
  die 'live home-activity test requires --approve-state-change and the interactive approval phrase'
fi
printf 'This test changes the default HOME activity temporarily, then attempts to restore it.\n'
printf 'Type APPROVE HOME-ACTIVITY %s to continue: ' "$TEST_ID"
read -r approval
[ "$approval" = "APPROVE HOME-ACTIVITY $TEST_ID" ] || die 'approval phrase did not match; no state-changing command was executed'

capture_state() {
  local phase="$1"
  run_adb_capture "${phase}_home_resolve" no "$OUTPUT/${phase}_home_resolve.txt" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user "$USER_ID"
  run_adb_capture "${phase}_home_query" no "$OUTPUT/${phase}_home_query.txt" shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user "$USER_ID"
  run_adb_capture "${phase}_preferred_activities" no "$OUTPUT/${phase}_preferred_activities.txt" shell dumpsys package preferred-activities
  run_adb_capture "${phase}_activity" no "$OUTPUT/${phase}_activity.txt" shell dumpsys activity activities
  run_adb_capture "${phase}_window" no "$OUTPUT/${phase}_window.txt" shell dumpsys window windows
}

printf 'test_id=%s\nserial=%s\nuser=%s\ntarget=%s\nrestore=%s\nstarted_utc=%s\n' \
  "$TEST_ID" "$SERIAL" "$USER_ID" "$TARGET" "$RESTORE" "$(timestamp_utc)" > "$OUTPUT/test_metadata.txt"

capture_state before

run_adb_capture 'set_target' yes "$OUTPUT/set_target.txt" shell cmd package set-home-activity --user "$USER_ID" "$TARGET"
target_status="$LAST_STATUS"
printf 'target_status=%s\n' "$target_status" >> "$OUTPUT/test_metadata.txt"

capture_state after_target

run_adb_capture 'set_restore' yes "$OUTPUT/set_restore.txt" shell cmd package set-home-activity --user "$USER_ID" "$RESTORE"
restore_status="$LAST_STATUS"
printf 'restore_status=%s\n' "$restore_status" >> "$OUTPUT/test_metadata.txt"

capture_state final

if command -v rg >/dev/null 2>&1; then
  rg -n 'priority=|isDefault=|mResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|com\\.amazon\\.firelauncher|com\\.microsoft\\.launcher' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
else
  grep -REn 'priority=|isDefault=|mResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|com\\.amazon\\.firelauncher|com\\.microsoft\\.launcher' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
fi

{
  printf '# HOME activity test summary\n\n'
  printf -- '- Test ID: `%s`\n' "$TEST_ID"
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- User: `%s`\n' "$USER_ID"
  printf -- '- Target: `%s`\n' "$TARGET"
  printf -- '- Restore target: `%s`\n' "$RESTORE"
  printf -- '- `set-home-activity` target exit status: `%s`\n' "$target_status"
  printf -- '- `set-home-activity` restore exit status: `%s`\n' "$restore_status"
  printf -- '- Causal finding: `Hypothesis` until before/after/final resolver states are reviewed.\n\n'
  printf 'The final resolver state is authoritative for whether the requested restore completed; command success alone is insufficient.\n'
} > "$OUTPUT/test_summary.md"

write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"
printf 'HOME activity test completed: %s\n' "$TEST_ID"
if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'HOME activity test completed with %s command failure(s); inspect %s\n' "$HARD_FAILURES" "$MANIFEST" >&2
  exit 2
fi
