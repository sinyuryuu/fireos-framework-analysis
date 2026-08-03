#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
TEST_ID=''
TARGET=''
RESTORE=''
PREP_COMPONENT='com.android.settings/.Settings'
ACTION='keyevent'
DURATION='5'
OUTPUT=''
APPROVE_STATE_CHANGE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: test_home_preferred_runtime.sh --serial SERIAL --test-id ID
       --target PACKAGE/ACTIVITY --restore PACKAGE/ACTIVITY --output DIR
       [--prepare PACKAGE/ACTIVITY] [--action keyevent|home-intent]
       [--duration SECONDS] [--approve-state-change] [--dry-run]

Temporarily writes a preferred HOME activity, starts a non-launcher activity,
probes Home, records resolver/foreground/logcat evidence, and restores the
supplied HOME activity. Live execution requires an interactive approval phrase.
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
    --prepare)
      [ "$#" -ge 2 ] || die '--prepare requires a value'
      PREP_COMPONENT="$2"
      shift 2
      ;;
    --action)
      [ "$#" -ge 2 ] || die '--action requires a value'
      ACTION="$2"
      shift 2
      ;;
    --duration)
      [ "$#" -ge 2 ] || die '--duration requires a value'
      DURATION="$2"
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
printf '%s' "$DURATION" | grep -Eq '^[1-9][0-9]*$' || die '--duration must be a positive integer'
case "$ACTION" in
  keyevent|home-intent) ;;
  *) die "unsupported action: $ACTION" ;;
esac

print_plan() {
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: serial=%s test-id=%s action=%s duration=%s output=%s\n' \
    "$SERIAL" "$TEST_ID" "$ACTION" "$DURATION" "$OUTPUT"
  printf "DRY-RUN: read-only snapshots: adb -s '%s' shell cmd package resolve-activity ...\n" "$SERIAL"
  printf "DRY-RUN: gated preferred target: adb -s '%s' shell cmd package set-home-activity '%s'\n" "$SERIAL" "$TARGET"
  printf "DRY-RUN: gated foreground prep: adb -s '%s' shell am start -n '%s'\n" "$SERIAL" "$PREP_COMPONENT"
  case "$ACTION" in
    keyevent) printf "DRY-RUN: gated Home probe: adb -s '%s' shell input keyevent 3\n" "$SERIAL" ;;
    home-intent) printf "DRY-RUN: gated Home probe: adb -s '%s' shell am start -a android.intent.action.MAIN -c android.intent.category.HOME\n" "$SERIAL" ;;
  esac
  printf "DRY-RUN: gated restore: adb -s '%s' shell cmd package set-home-activity '%s'\n" "$SERIAL" "$RESTORE"
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
  die 'live preferred-runtime test requires --approve-state-change and the interactive approval phrase'
fi
printf 'This test temporarily changes the preferred HOME activity and foreground application, then restores the supplied HOME activity.\n'
printf 'Type APPROVE HOME-PROBE %s to continue: ' "$TEST_ID"
read -r approval
[ "$approval" = "APPROVE HOME-PROBE $TEST_ID" ] || die 'approval phrase did not match; no state-changing command was executed'

capture_state() {
  local phase="$1"
  run_adb_capture "${phase}_home_resolve" no "$OUTPUT/${phase}_home_resolve.txt" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
  run_adb_capture "${phase}_home_query" no "$OUTPUT/${phase}_home_query.txt" shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME
  run_adb_capture "${phase}_preferred_activities" no "$OUTPUT/${phase}_preferred_activities.txt" shell dumpsys package preferred-activities
  run_adb_capture "${phase}_activity" no "$OUTPUT/${phase}_activity.txt" shell dumpsys activity activities
  run_adb_capture "${phase}_window" no "$OUTPUT/${phase}_window.txt" shell dumpsys window windows
}

printf 'test_id=%s\nserial=%s\ntarget=%s\nrestore=%s\nprepare=%s\naction=%s\nduration_seconds=%s\nstarted_utc=%s\n' \
  "$TEST_ID" "$SERIAL" "$TARGET" "$RESTORE" "$PREP_COMPONENT" "$ACTION" "$DURATION" "$(timestamp_utc)" > "$OUTPUT/test_metadata.txt"

capture_state before
run_adb_capture 'set_target' yes "$OUTPUT/set_target.txt" shell cmd package set-home-activity "$TARGET"
target_status="$LAST_STATUS"
printf 'target_status=%s\n' "$target_status" >> "$OUTPUT/test_metadata.txt"
capture_state after_target

run_adb_capture 'prepare_foreground' yes "$OUTPUT/prepare_foreground.txt" shell am start -n "$PREP_COMPONENT"
sleep 2
capture_state before_home_probe

run_adb_capture 'logcat_clear' yes "$OUTPUT/logcat_clear.txt" logcat -c
if [ "$LAST_STATUS" -ne 0 ]; then
  die 'logcat clear failed; Home probe stopped before the action'
fi

LOGCAT_FULL="$OUTPUT/logcat_full.txt"
LOGCAT_FOCUS="$OUTPUT/logcat_focus.txt"
adb -s "$SERIAL" logcat -b all -v threadtime > "$LOGCAT_FULL" 2>&1 &
FULL_LOG_PID=$!
adb -s "$SERIAL" logcat -b all -v threadtime \
  ActivityManager:I ActivityTaskManager:I WindowManager:I PackageManager:I \
  InputDispatcher:I InputReader:I PhoneWindowManager:I SystemUI:I 'Amazon*:V' '*:S' \
  > "$LOGCAT_FOCUS" 2>&1 &
FOCUS_LOG_PID=$!

cleanup_logs() {
  kill "$FULL_LOG_PID" "$FOCUS_LOG_PID" 2>/dev/null || true
  wait "$FULL_LOG_PID" 2>/dev/null || true
  wait "$FOCUS_LOG_PID" 2>/dev/null || true
}
trap cleanup_logs EXIT

action_started=$(timestamp_utc)
case "$ACTION" in
  keyevent)
    run_adb_capture 'action_keyevent_home' yes "$OUTPUT/action.txt" shell input keyevent 3
    action_command='adb -s SERIAL shell input keyevent 3'
    ;;
  home-intent)
    run_adb_capture 'action_home_intent' yes "$OUTPUT/action.txt" shell am start -a android.intent.action.MAIN -c android.intent.category.HOME
    action_command='adb -s SERIAL shell am start -a android.intent.action.MAIN -c android.intent.category.HOME'
    ;;
esac
action_status="$LAST_STATUS"
action_finished=$(timestamp_utc)
printf 'action_started_utc=%s\naction_finished_utc=%s\naction_command=%s\naction_status=%s\n' \
  "$action_started" "$action_finished" "$action_command" "$action_status" >> "$OUTPUT/test_metadata.txt"

sleep "$DURATION"
capture_state after_home_probe
cleanup_logs
trap - EXIT

run_adb_capture 'set_restore' yes "$OUTPUT/set_restore.txt" shell cmd package set-home-activity "$RESTORE"
restore_status="$LAST_STATUS"
printf 'restore_status=%s\n' "$restore_status" >> "$OUTPUT/test_metadata.txt"
capture_state final

if command -v rg >/dev/null 2>&1; then
  rg -n 'priority=|isDefault=|mResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|realActivity|origActivity|cmp=|com\\.amazon\\.firelauncher|com\\.microsoft\\.launcher' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
else
  grep -REn 'priority=|isDefault=|mResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|realActivity|origActivity|cmp=|com\\.amazon\\.firelauncher|com\\.microsoft\\.launcher' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
fi

{
  printf '# Preferred HOME runtime probe summary\n\n'
  printf -- '- Test ID: `%s`\n' "$TEST_ID"
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- Preferred target: `%s`\n' "$TARGET"
  printf -- '- Restore target: `%s`\n' "$RESTORE"
  printf -- '- Preparation component: `%s`\n' "$PREP_COMPONENT"
  printf -- '- Home action: `%s`\n' "$ACTION"
  printf -- '- `set-home-activity` target exit status: `%s`\n' "$target_status"
  printf -- '- Home action exit status: `%s`\n' "$action_status"
  printf -- '- `set-home-activity` restore exit status: `%s`\n' "$restore_status"
  printf -- '- Causal status: `Hypothesis` until the resolver, foreground, and logcat snapshots are reviewed.\n\n'
  printf 'The final resolver state is authoritative for whether restoration completed.\n'
} > "$OUTPUT/test_summary.md"

write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"
printf 'Preferred HOME runtime probe completed: %s\n' "$TEST_ID"
if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'Preferred HOME runtime probe completed with %s command failure(s); inspect %s\n' "$HARD_FAILURES" "$MANIFEST" >&2
  exit 2
fi
