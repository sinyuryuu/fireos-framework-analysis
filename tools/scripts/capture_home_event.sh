#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
TEST_ID=''
DURATION=''
OUTPUT=''
ACTION='manual'
COMPONENT=''
PREPARE_COMPONENT=''
WAKE_SCREEN=0
DISMISS_KEYGUARD=0
CLEAR_LOGCAT=0
APPROVE_STATE_CHANGE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: capture_home_event.sh --serial SERIAL --test-id HOME-TNN --duration SECONDS --output DIR
       [--action manual|keyevent|home-intent|explicit] [--component PACKAGE/ACTIVITY]
       [--prepare PACKAGE/ACTIVITY]
       [--wake]
       [--dismiss-keyguard]
       [--clear-logcat] [--approve-state-change] [--dry-run]

Captures before/after state and logcat around one Home-related action.
Live actions require an interactive approval gate. Dry-run performs no ADB calls.
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
    --action)
      [ "$#" -ge 2 ] || die '--action requires a value'
      ACTION="$2"
      shift 2
      ;;
    --component)
      [ "$#" -ge 2 ] || die '--component requires a value'
      COMPONENT="$2"
      shift 2
      ;;
    --prepare)
      [ "$#" -ge 2 ] || die '--prepare requires a value'
      PREPARE_COMPONENT="$2"
      shift 2
      ;;
    --wake) WAKE_SCREEN=1; shift ;;
    --dismiss-keyguard) DISMISS_KEYGUARD=1; shift ;;
    --clear-logcat) CLEAR_LOGCAT=1; shift ;;
    --approve-state-change) APPROVE_STATE_CHANGE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$DURATION" ] || die '--duration is required'
[ -n "$OUTPUT" ] || die '--output is required'
printf '%s' "$TEST_ID" | grep -Eq '^HOME-T[0-9]{2,}$' || die '--test-id must match HOME-TNN'
printf '%s' "$DURATION" | grep -Eq '^[1-9][0-9]*$' || die '--duration must be a positive integer'
case "$ACTION" in
  manual|keyevent|home-intent|explicit) ;;
  *) die "unsupported action: $ACTION" ;;
esac
if [ "$ACTION" = 'explicit' ] && [ -z "$COMPONENT" ]; then
  die '--component is required for --action explicit'
fi

print_plan() {
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: serial=%s test-id=%s duration=%s action=%s output=%s\n' "$SERIAL" "$TEST_ID" "$DURATION" "$ACTION" "$OUTPUT"
  if [ -n "$PREPARE_COMPONENT" ]; then
    printf "DRY-RUN: gated foreground preparation: adb -s '%s' shell am start -n '%s'\n" "$SERIAL" "$PREPARE_COMPONENT"
  fi
  if [ "$WAKE_SCREEN" -eq 1 ]; then
    printf "DRY-RUN: gated wake command: adb -s '%s' shell input keyevent 224\n" "$SERIAL"
  fi
  if [ "$DISMISS_KEYGUARD" -eq 1 ]; then
    printf "DRY-RUN: gated keyguard gesture: adb -s '%s' shell input swipe 600 1800 600 400 300\n" "$SERIAL"
  fi
  if [ "$CLEAR_LOGCAT" -eq 1 ]; then
    printf "DRY-RUN: gated command: adb -s '%s' logcat -c\n" "$SERIAL"
  fi
  printf 'DRY-RUN: read-only snapshots: dumpsys activity activities, recents, window windows, input, package\n'
  printf "DRY-RUN: stream: adb -s '%s' logcat -b all -v threadtime\n" "$SERIAL"
  case "$ACTION" in
    manual) printf 'DRY-RUN: gated manual action: researcher presses the physical Home key once\n' ;;
    keyevent) printf "DRY-RUN: gated command: adb -s '%s' shell input keyevent 3\n" "$SERIAL" ;;
    home-intent) printf "DRY-RUN: gated command: adb -s '%s' shell am start -a android.intent.action.MAIN -c android.intent.category.HOME\n" "$SERIAL" ;;
    explicit) printf "DRY-RUN: gated command: adb -s '%s' shell am start -n '%s'\n" "$SERIAL" "$COMPONENT" ;;
  esac
  printf 'DRY-RUN: after-action snapshots, tag counts, summary and SHA-256 manifest would be written under %s\n' "$OUTPUT"
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
  die 'live capture requires --approve-state-change and the interactive approval phrase'
fi
printf 'This capture can change the foreground UI and may clear the log buffer.\n'
printf 'Type APPROVE %s to continue: ' "$TEST_ID"
read -r approval
[ "$approval" = "APPROVE $TEST_ID" ] || die 'approval phrase did not match; no live action was executed'

if [ "$CLEAR_LOGCAT" -eq 1 ]; then
  run_adb_capture 'logcat_clear' yes "$OUTPUT/logcat_clear.txt" logcat -c
  [ "$LAST_STATUS" -eq 0 ] || die 'logcat clear failed; capture stopped before the Home action'
fi

printf 'test_id=%s\nserial=%s\naction=%s\nprepare=%s\nwake_screen=%s\ndismiss_keyguard=%s\nduration_seconds=%s\nstarted_utc=%s\nlogcat_cleared=%s\n' \
  "$TEST_ID" "$SERIAL" "$ACTION" "${PREPARE_COMPONENT:-none}" "$WAKE_SCREEN" "$DISMISS_KEYGUARD" "$DURATION" "$(timestamp_utc)" "$CLEAR_LOGCAT" > "$OUTPUT/test_metadata.txt"

capture_snapshot() {
  local phase="$1"
  run_adb_capture "${phase}_activity_activities" no "$OUTPUT/${phase}_activity_activities.txt" shell dumpsys activity activities
  run_adb_capture "${phase}_activity_recents" no "$OUTPUT/${phase}_activity_recents.txt" shell dumpsys activity recents
  run_adb_capture "${phase}_window_windows" no "$OUTPUT/${phase}_window_windows.txt" shell dumpsys window windows
  run_adb_capture "${phase}_input" no "$OUTPUT/${phase}_input.txt" shell dumpsys input
  run_adb_capture "${phase}_package" no "$OUTPUT/${phase}_package.txt" shell dumpsys package
}

capture_snapshot before

if [ "$WAKE_SCREEN" -eq 1 ]; then
  run_adb_capture 'wake_screen' yes "$OUTPUT/wake_screen.txt" shell input keyevent 224
  sleep 2
  capture_snapshot after_wake
fi

if [ "$DISMISS_KEYGUARD" -eq 1 ]; then
  run_adb_capture 'dismiss_keyguard' yes "$OUTPUT/dismiss_keyguard.txt" shell input swipe 600 1800 600 400 300
  sleep 2
  capture_snapshot after_keyguard_dismiss
fi

if [ -n "$PREPARE_COMPONENT" ]; then
  run_adb_capture 'prepare_foreground' yes "$OUTPUT/prepare_foreground.txt" shell am start -n "$PREPARE_COMPONENT"
  sleep 2
  capture_snapshot before_action
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
manual_ack_utc=''
case "$ACTION" in
  manual)
    printf 'Press the physical Home key once, then press Enter here.\n'
    read -r _manual_ack
    manual_ack_utc=$(timestamp_utc)
    action_started="$manual_ack_utc"
    action_command='manual physical Home key'
    action_status=0
    ;;
  keyevent)
    run_adb_capture 'action_keyevent_home' yes "$OUTPUT/action.txt" shell input keyevent 3
    action_status="$LAST_STATUS"
    action_command='adb -s SERIAL shell input keyevent 3'
    ;;
  home-intent)
    run_adb_capture 'action_home_intent' yes "$OUTPUT/action.txt" shell am start -a android.intent.action.MAIN -c android.intent.category.HOME
    action_status="$LAST_STATUS"
    action_command='adb -s SERIAL shell am start -a android.intent.action.MAIN -c android.intent.category.HOME'
    ;;
  explicit)
    run_adb_capture 'action_explicit_activity' yes "$OUTPUT/action.txt" shell am start -n "$COMPONENT"
    action_status="$LAST_STATUS"
    action_command="adb -s SERIAL shell am start -n $COMPONENT"
    ;;
esac
action_finished=$(timestamp_utc)
printf 'action_started_utc=%s\naction_finished_utc=%s\naction_ack_utc=%s\naction_command=%s\naction_status=%s\n' \
  "$action_started" "$action_finished" "$manual_ack_utc" "$action_command" "$action_status" >> "$OUTPUT/test_metadata.txt"

sleep "$DURATION"
capture_snapshot after
cleanup_logs
trap - EXIT

if command -v awk >/dev/null 2>&1; then
  awk 'NF >= 6 { tag=$6; sub(/:$/, "", tag); if (tag != "") count[tag]++ } END { for (tag in count) print count[tag] "\t" tag }' \
    "$LOGCAT_FULL" | sort -nr > "$OUTPUT/logcat_tag_counts.tsv" || true
fi

if command -v rg >/dev/null 2>&1; then
  rg -n 'mResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|realActivity|origActivity|cmp=' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
else
  grep -REn 'mResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|realActivity|origActivity|cmp=' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
fi

{
  printf '# Home event test summary\n\n'
  printf -- '- Test ID: `%s`\n' "$TEST_ID"
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- Action: `%s`\n' "$ACTION"
  printf -- '- Foreground preparation: `%s`\n' "${PREPARE_COMPONENT:-none}"
  printf -- '- Wake screen before preparation: `%s`\n' "$WAKE_SCREEN"
  printf -- '- Dismiss keyguard before preparation: `%s`\n' "$DISMISS_KEYGUARD"
  printf -- '- Duration after action: `%s` seconds\n' "$DURATION"
  printf -- '- Logcat cleared: `%s`\n' "$CLEAR_LOGCAT"
  printf -- '- Action command status: `%s`\n' "$action_status"
  printf -- '- Finding status: `Hypothesis` for causal interpretation; raw state changes are observations.\n\n'
  printf '## Evidence\n\n'
  printf -- '- [Command manifest](command_manifest.tsv)\n'
  printf -- '- [Before/after state focus](state_focus_lines.txt)\n'
  printf -- '- [Full logcat](logcat_full.txt)\n'
  printf -- '- [Focused logcat](logcat_focus.txt)\n'
  printf -- '- [SHA-256 manifest](sha256sums.txt)\n\n'
  printf 'No conclusion about PackageManager, SystemUI, Framework or watchdog behavior is generated automatically.\n'
} > "$OUTPUT/test_summary.md"

write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"
printf 'Home event capture completed: %s\n' "$TEST_ID"
