#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
TEST_ID=''
OUTPUT=''
ROUTE='subsettings'
FRAGMENT='com.android.settings.applications.defaultapps.DefaultHomePicker'
DURATION='5'
APPROVE_STATE_CHANGE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: probe_settings_home_picker.sh --serial SERIAL --test-id SETTINGS-TNN --output DIR
       [--route subsettings|advanced] [--fragment CLASS]
       [--duration SECONDS] [--approve-state-change] [--dry-run]

Attempts to open a Settings fragment without selecting a launcher or writing
default-app state. The default fragment is Android's retained
DefaultHomePicker. The probe records whether Settings accepts or rejects the
fragment, captures the resulting UI/activity state, and restores Home.
Live execution changes only foreground state and requires an interactive
approval phrase.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial)
      [ "$#" -ge 2 ] || die '--serial requires a value'
      SERIAL="$2"; shift 2 ;;
    --test-id)
      [ "$#" -ge 2 ] || die '--test-id requires a value'
      TEST_ID="$2"; shift 2 ;;
    --output)
      [ "$#" -ge 2 ] || die '--output requires a path'
      OUTPUT="$2"; shift 2 ;;
    --route)
      [ "$#" -ge 2 ] || die '--route requires a value'
      ROUTE="$2"; shift 2 ;;
    --fragment)
      [ "$#" -ge 2 ] || die '--fragment requires a value'
      FRAGMENT="$2"; shift 2 ;;
    --duration)
      [ "$#" -ge 2 ] || die '--duration requires a value'
      DURATION="$2"; shift 2 ;;
    --approve-state-change) APPROVE_STATE_CHANGE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$OUTPUT" ] || die '--output is required'
printf '%s' "$TEST_ID" | grep -Eq '^SETTINGS-T[0-9]{2,}$' || die '--test-id must match SETTINGS-TNN'
printf '%s' "$ROUTE" | grep -Eq '^(subsettings|advanced)$' || die '--route must be subsettings or advanced'
printf '%s' "$DURATION" | grep -Eq '^[1-9][0-9]*$' || die '--duration must be a positive integer'
printf '%s' "$FRAGMENT" | grep -Eq '^[A-Za-z0-9_$.]+$' || die '--fragment must be a Java class name'

case "$ROUTE" in
  subsettings) ACTIVITY='com.android.settings/.SubSettings' ;;
  # adb shell reconstructs the command for the remote shell; escape the
  # nested-class dollar sign so it is not expanded as a shell variable.
  advanced) ACTIVITY='com.android.settings/.Settings\$AdvancedAppsActivity' ;;
esac

print_plan() {
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: serial=%s test-id=%s route=%s activity=%s fragment=%s duration=%s output=%s\n' \
    "$SERIAL" "$TEST_ID" "$ROUTE" "$ACTIVITY" "$FRAGMENT" "$DURATION" "$OUTPUT"
  printf "DRY-RUN: gated wake: adb -s '%s' shell input keyevent 224\n" "$SERIAL"
  printf "DRY-RUN: gated keyguard gesture: adb -s '%s' shell input swipe 600 1800 600 400 300\n" "$SERIAL"
  printf "DRY-RUN: gated fragment start: adb -s '%s' shell am start -n '%s' --es :settings:show_fragment '%s'\n" "$SERIAL" "$ACTIVITY" "$FRAGMENT"
  printf "DRY-RUN: temporary UI dump/readback/cleanup uses /sdcard/codex-settings-picker-%s.xml\n" "$TEST_ID"
  printf "DRY-RUN: gated restore: adb -s '%s' shell input keyevent 3\n" "$SERIAL"
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

[ "$APPROVE_STATE_CHANGE" -eq 1 ] || die 'live Settings fragment probe requires --approve-state-change and the interactive approval phrase'
printf 'This probe changes foreground state, wakes the screen, dismisses keyguard and returns Home afterward.\n'
printf 'Type APPROVE %s to continue: ' "$TEST_ID"
read -r approval
[ "$approval" = "APPROVE $TEST_ID" ] || die 'approval phrase did not match; no state-changing command was executed'

printf 'test_id=%s\nserial=%s\nroute=%s\nactivity=%s\nfragment=%s\nduration_seconds=%s\nstarted_utc=%s\n' \
  "$TEST_ID" "$SERIAL" "$ROUTE" "$ACTIVITY" "$FRAGMENT" "$DURATION" "$(timestamp_utc)" > "$OUTPUT/test_metadata.txt"

capture_snapshot() {
  local phase="$1"
  run_adb_capture "${phase}_activity" no "$OUTPUT/${phase}_activity.txt" shell dumpsys activity activities
  run_adb_capture "${phase}_window" no "$OUTPUT/${phase}_window.txt" shell dumpsys window windows
}

capture_snapshot before
run_adb_capture 'wake_screen' yes "$OUTPUT/wake_screen.txt" shell input keyevent 224
sleep 2
run_adb_capture 'dismiss_keyguard' yes "$OUTPUT/dismiss_keyguard.txt" shell input swipe 600 1800 600 400 300
sleep 2
capture_snapshot after_keyguard_dismiss

run_adb_capture 'logcat_clear' yes "$OUTPUT/logcat_clear.txt" logcat -c
LOGCAT_FULL="$OUTPUT/logcat_full.txt"
LOGCAT_FOCUS="$OUTPUT/logcat_focus.txt"
adb -s "$SERIAL" logcat -b all -v threadtime > "$LOGCAT_FULL" 2>&1 &
FULL_LOG_PID=$!
adb -s "$SERIAL" logcat -b all -v threadtime \
  ActivityManager:I ActivityTaskManager:I WindowManager:I PackageManager:I \
  SettingsActivity:D 'AndroidRuntime:E' 'System.err:E' '*:S' \
  > "$LOGCAT_FOCUS" 2>&1 &
FOCUS_LOG_PID=$!

cleanup_logs() {
  kill "$FULL_LOG_PID" "$FOCUS_LOG_PID" 2>/dev/null || true
  wait "$FULL_LOG_PID" 2>/dev/null || true
  wait "$FOCUS_LOG_PID" 2>/dev/null || true
}
trap cleanup_logs EXIT

run_adb_capture 'open_fragment' no "$OUTPUT/open_fragment.txt" shell am start -n "$ACTIVITY" --es :settings:show_fragment "$FRAGMENT" --ez :settings:show_fragment_as_subsetting true
open_status="$LAST_STATUS"
sleep "$DURATION"
capture_snapshot after_fragment
DEVICE_UI_DUMP="/sdcard/codex-settings-picker-${TEST_ID}.xml"
run_adb_capture 'fragment_ui_dump' no "$OUTPUT/fragment_ui_dump.txt" shell uiautomator dump "$DEVICE_UI_DUMP"
run_adb_capture 'fragment_ui_readback' no "$OUTPUT/fragment_ui.xml" shell cat "$DEVICE_UI_DUMP"
run_adb_capture 'fragment_ui_cleanup' no "$OUTPUT/fragment_ui_cleanup.txt" shell rm "$DEVICE_UI_DUMP"
run_adb_capture 'restore_home' yes "$OUTPUT/restore_home.txt" shell input keyevent 3
restore_status="$LAST_STATUS"
sleep 3
capture_snapshot after_restore
cleanup_logs
trap - EXIT

if command -v rg >/dev/null 2>&1; then
  rg -n 'mResumedActivity|ResumedActivity|topResumedActivity|mCurrentFocus|mFocusedApp|Invalid fragment|DefaultHomePicker|DefaultAppSettings|AndroidRuntime|com\.android\.settings|com\.amazon\.firelauncher' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
else
  grep -REn 'mResumedActivity|ResumedActivity|topResumedActivity|mCurrentFocus|mFocusedApp|Invalid fragment|DefaultHomePicker|DefaultAppSettings|AndroidRuntime|com\.android\.settings|com\.amazon\.firelauncher' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
fi

printf 'open_fragment_status=%s\nrestore_home_status=%s\nfinished_utc=%s\n' \
  "$open_status" "$restore_status" "$(timestamp_utc)" >> "$OUTPUT/test_metadata.txt"

{
  printf '# Settings Home picker probe summary\n\n'
  printf -- '- Test ID: `%s`\n' "$TEST_ID"
  printf -- '- Route: `%s`\n' "$ROUTE"
  printf -- '- Activity: `%s`\n' "$ACTIVITY"
  printf -- '- Fragment: `%s`\n' "$FRAGMENT"
  printf -- '- Fragment start status: `%s` (a rejection may be expected for an invalid fragment)\n' "$open_status"
  printf -- '- Restore Home status: `%s`\n' "$restore_status"
  printf -- '- Finding status: `Hypothesis` until raw activity/logcat/UI outputs are reviewed.\n\n'
  printf '## Evidence\n\n'
  printf -- '- [Command manifest](command_manifest.tsv)\n'
  printf -- '- [Fragment start output](open_fragment.txt)\n'
  printf -- '- [Fragment UI dump](fragment_ui.xml)\n'
  printf -- '- [Focused state lines](state_focus_lines.txt)\n'
  printf -- '- [Focused logcat](logcat_focus.txt)\n'
  printf -- '- [SHA-256 manifest](sha256sums.txt)\n\n'
  printf 'The probe never selects a launcher, calls a package-state mutation, or writes default-app data.\n'
} > "$OUTPUT/test_summary.md"

write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"
printf 'Settings Home picker probe completed: %s\n' "$TEST_ID"
if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'Settings Home picker probe completed with %s required command failure(s); inspect %s\n' "$HARD_FAILURES" "$MANIFEST" >&2
  exit 2
fi
