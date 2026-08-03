#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
TEST_ID=''
OUTPUT=''
DURATION='5'
APPROVE_STATE_CHANGE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: probe_home_settings.sh --serial SERIAL --test-id HOME-TNN --output DIR
       [--duration SECONDS] [--approve-state-change] [--dry-run]

Opens the standard android.settings.HOME_SETTINGS entrypoint, records the
resulting Settings activity and UI hierarchy, then returns to the resolver's
Home activity. It uses one uniquely named temporary UI-dump file on the device
and removes that same file after reading it. It does not select a launcher,
write settings, clear data, disable packages, or reboot.
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
    --output)
      [ "$#" -ge 2 ] || die '--output requires a path'
      OUTPUT="$2"
      shift 2
      ;;
    --duration)
      [ "$#" -ge 2 ] || die '--duration requires a value'
      DURATION="$2"
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
[ -n "$OUTPUT" ] || die '--output is required'
printf '%s' "$TEST_ID" | grep -Eq '^HOME-T[0-9]{2,}$' || die '--test-id must match HOME-TNN'
printf '%s' "$DURATION" | grep -Eq '^[1-9][0-9]*$' || die '--duration must be a positive integer'

print_plan() {
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: serial=%s test-id=%s duration=%s output=%s\n' "$SERIAL" "$TEST_ID" "$DURATION" "$OUTPUT"
  printf "DRY-RUN: gated wake: adb -s '%s' shell input keyevent 224\n" "$SERIAL"
  printf "DRY-RUN: gated keyguard gesture: adb -s '%s' shell input swipe 600 1800 600 400 300\n" "$SERIAL"
  printf "DRY-RUN: gated Settings intent: adb -s '%s' shell am start -a android.settings.HOME_SETTINGS\n" "$SERIAL"
  printf "DRY-RUN: temporary UI dump: adb -s '%s' shell uiautomator dump /sdcard/codex-home-settings-%s.xml\n" "$SERIAL" "$TEST_ID"
  printf "DRY-RUN: read temporary UI dump: adb -s '%s' shell cat /sdcard/codex-home-settings-%s.xml\n" "$SERIAL" "$TEST_ID"
  printf "DRY-RUN: remove temporary UI dump: adb -s '%s' shell rm /sdcard/codex-home-settings-%s.xml\n" "$SERIAL" "$TEST_ID"
  printf "DRY-RUN: gated restore: adb -s '%s' shell input keyevent 3\n" "$SERIAL"
  printf 'DRY-RUN: snapshots, logcat, summary and SHA-256 manifest would be written under %s\n' "$OUTPUT"
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
  die 'live Settings probe requires --approve-state-change and the interactive approval phrase'
fi
printf 'This probe changes foreground state, wakes the screen, dismisses keyguard and returns Home afterward.\n'
printf 'Type APPROVE %s to continue: ' "$TEST_ID"
read -r approval
[ "$approval" = "APPROVE $TEST_ID" ] || die 'approval phrase did not match; no state-changing command was executed'

printf 'test_id=%s\nserial=%s\nduration_seconds=%s\nstarted_utc=%s\n' \
  "$TEST_ID" "$SERIAL" "$DURATION" "$(timestamp_utc)" > "$OUTPUT/test_metadata.txt"

capture_snapshot() {
  local phase="$1"
  run_adb_capture "${phase}_resolver" no "$OUTPUT/${phase}_resolver.txt" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
  run_adb_capture "${phase}_activity" no "$OUTPUT/${phase}_activity.txt" shell dumpsys activity activities
  run_adb_capture "${phase}_window" no "$OUTPUT/${phase}_window.txt" shell dumpsys window windows
  run_adb_capture "${phase}_input" no "$OUTPUT/${phase}_input.txt" shell dumpsys input
}

capture_snapshot before
run_adb_capture 'wake_screen' yes "$OUTPUT/wake_screen.txt" shell input keyevent 224
sleep 2
capture_snapshot after_wake
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
  InputDispatcher:I InputReader:I PhoneWindowManager:I SystemUI:I 'Amazon*:V' '*:S' \
  > "$LOGCAT_FOCUS" 2>&1 &
FOCUS_LOG_PID=$!

cleanup_logs() {
  kill "$FULL_LOG_PID" "$FOCUS_LOG_PID" 2>/dev/null || true
  wait "$FULL_LOG_PID" 2>/dev/null || true
  wait "$FOCUS_LOG_PID" 2>/dev/null || true
}
trap cleanup_logs EXIT

run_adb_capture 'open_home_settings' yes "$OUTPUT/open_home_settings.txt" shell am start -a android.settings.HOME_SETTINGS
open_status="$LAST_STATUS"
sleep "$DURATION"
capture_snapshot settings
DEVICE_UI_DUMP="/sdcard/codex-home-settings-${TEST_ID}.xml"
run_adb_capture 'settings_ui_dump' yes "$OUTPUT/settings_ui_dump.txt" shell uiautomator dump "$DEVICE_UI_DUMP"
run_adb_capture 'settings_ui_readback' yes "$OUTPUT/settings_ui.xml" shell cat "$DEVICE_UI_DUMP"
run_adb_capture 'settings_ui_cleanup' yes "$OUTPUT/settings_ui_cleanup.txt" shell rm "$DEVICE_UI_DUMP"
run_adb_capture 'restore_home' yes "$OUTPUT/restore_home.txt" shell input keyevent 3
restore_status="$LAST_STATUS"
sleep 3
capture_snapshot after_restore
cleanup_logs
trap - EXIT

if command -v awk >/dev/null 2>&1; then
  awk 'NF >= 6 { tag=$6; sub(/:$/, "", tag); if (tag != "") count[tag]++ } END { for (tag in count) print count[tag] "\t" tag }' \
    "$LOGCAT_FULL" | sort -nr > "$OUTPUT/logcat_tag_counts.tsv" || true
fi

if command -v rg >/dev/null 2>&1; then
  rg -n 'mResumedActivity|ResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|realActivity|origActivity|com\.android\.settings|com\.amazon\.firelauncher|HOME_SETTINGS' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
else
  grep -REn 'mResumedActivity|ResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|realActivity|origActivity|com\.android\.settings|com\.amazon\.firelauncher|HOME_SETTINGS' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
fi

printf 'open_home_settings_status=%s\nrestore_home_status=%s\nfinished_utc=%s\n' \
  "$open_status" "$restore_status" "$(timestamp_utc)" >> "$OUTPUT/test_metadata.txt"

{
  printf '# Settings Home entrypoint probe summary\n\n'
  printf -- '- Test ID: `%s`\n' "$TEST_ID"
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- Settings intent: `android.settings.HOME_SETTINGS`\n'
  printf -- '- Open command status: `%s`\n' "$open_status"
  printf -- '- Restore Home status: `%s`\n' "$restore_status"
  printf -- '- Finding status: `Hypothesis` until activity/UI outputs are reviewed.\n\n'
  printf '## Evidence\n\n'
  printf -- '- [Command manifest](command_manifest.tsv)\n'
  printf -- '- [Settings UI dump](settings_ui.xml)\n'
  printf -- '- [State focus lines](state_focus_lines.txt)\n'
  printf -- '- [Focused logcat](logcat_focus.txt)\n'
  printf -- '- [SHA-256 manifest](sha256sums.txt)\n\n'
  printf 'The probe does not select a launcher or write default-home settings; it only opens the exported Settings entrypoint and restores Home.\n'
} > "$OUTPUT/test_summary.md"

write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"
printf 'Settings Home probe completed: %s\n' "$TEST_ID"
if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'Settings Home probe completed with %s required command failure(s); inspect %s\n' "$HARD_FAILURES" "$MANIFEST" >&2
  exit 2
fi
