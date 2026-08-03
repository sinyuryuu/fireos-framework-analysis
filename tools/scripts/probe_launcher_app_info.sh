#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
TEST_ID=''
PACKAGE='com.amazon.firelauncher'
OUTPUT=''
DURATION='5'
TAP_HOME_ROW=0
TAP_X=''
TAP_Y=''
APPROVE_STATE_CHANGE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: probe_launcher_app_info.sh --serial SERIAL --test-id HOME-TNN --output DIR
       [--package PACKAGE] [--duration SECONDS]
       [--tap-home-row --tap-x X --tap-y Y]
       [--approve-state-change] [--dry-run]

Opens android.settings.APPLICATION_DETAILS_SETTINGS for the specified package,
records the Settings activity and UI hierarchy, then returns to Home. It does
not click a preference by default, write settings, clear data, disable
packages, reboot, or change the package. With --tap-home-row it taps only the
visible Home-app row and records the resulting screen; it still does not
select a launcher or write the default. It removes its uniquely named
temporary UI dumps after reading them. Live execution requires an interactive
approval phrase.
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
    --package)
      [ "$#" -ge 2 ] || die '--package requires a value'
      PACKAGE="$2"
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
    --tap-home-row) TAP_HOME_ROW=1; shift ;;
    --tap-x)
      [ "$#" -ge 2 ] || die '--tap-x requires a value'
      TAP_X="$2"
      shift 2
      ;;
    --tap-y)
      [ "$#" -ge 2 ] || die '--tap-y requires a value'
      TAP_Y="$2"
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
printf '%s' "$PACKAGE" | grep -Eq '^[A-Za-z0-9_.]+$' || die '--package must be a package name'
if [ "$TAP_HOME_ROW" -eq 1 ]; then
  [ -n "$TAP_X" ] || die '--tap-home-row requires --tap-x'
  [ -n "$TAP_Y" ] || die '--tap-home-row requires --tap-y'
  printf '%s' "$TAP_X" | grep -Eq '^[0-9]+$' || die '--tap-x must be a non-negative integer'
  printf '%s' "$TAP_Y" | grep -Eq '^[0-9]+$' || die '--tap-y must be a non-negative integer'
else
  [ -z "$TAP_X" ] || die '--tap-x requires --tap-home-row'
  [ -z "$TAP_Y" ] || die '--tap-y requires --tap-home-row'
fi

print_plan() {
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: serial=%s test-id=%s package=%s duration=%s output=%s tap_home_row=%s\n' "$SERIAL" "$TEST_ID" "$PACKAGE" "$DURATION" "$OUTPUT" "$TAP_HOME_ROW"
  printf "DRY-RUN: gated wake: adb -s '%s' shell input keyevent 224\n" "$SERIAL"
  printf "DRY-RUN: gated keyguard gesture: adb -s '%s' shell input swipe 600 1800 600 400 300\n" "$SERIAL"
  printf "DRY-RUN: gated App info intent: adb -s '%s' shell am start -a android.settings.APPLICATION_DETAILS_SETTINGS -d package:%s\n" "$SERIAL" "$PACKAGE"
  printf "DRY-RUN: temporary UI dump/readback/cleanup uses /sdcard/codex-app-info-%s.xml\n" "$TEST_ID"
  if [ "$TAP_HOME_ROW" -eq 1 ]; then
    printf "DRY-RUN: gated Home-app row tap: adb -s '%s' shell input tap %s %s\n" "$SERIAL" "$TAP_X" "$TAP_Y"
    printf "DRY-RUN: temporary post-tap UI dump/readback/cleanup uses /sdcard/codex-app-info-%s-after-tap.xml\n" "$TEST_ID"
  fi
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
  die 'live App info probe requires --approve-state-change and the interactive approval phrase'
fi
printf 'This probe changes foreground state, wakes the screen, dismisses keyguard and returns Home afterward.\n'
printf 'Type APPROVE %s to continue: ' "$TEST_ID"
read -r approval
[ "$approval" = "APPROVE $TEST_ID" ] || die 'approval phrase did not match; no state-changing command was executed'

printf 'test_id=%s\nserial=%s\npackage=%s\nduration_seconds=%s\nstarted_utc=%s\n' \
  "$TEST_ID" "$SERIAL" "$PACKAGE" "$DURATION" "$(timestamp_utc)" > "$OUTPUT/test_metadata.txt"

capture_snapshot() {
  local phase="$1"
  run_adb_capture "${phase}_activity" no "$OUTPUT/${phase}_activity.txt" shell dumpsys activity activities
  run_adb_capture "${phase}_window" no "$OUTPUT/${phase}_window.txt" shell dumpsys window windows
  run_adb_capture "${phase}_package" no "$OUTPUT/${phase}_package.txt" shell dumpsys package "$PACKAGE"
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

run_adb_capture 'open_app_info' yes "$OUTPUT/open_app_info.txt" shell am start -a android.settings.APPLICATION_DETAILS_SETTINGS -d "package:$PACKAGE"
open_status="$LAST_STATUS"
sleep "$DURATION"
capture_snapshot app_info
DEVICE_UI_DUMP="/sdcard/codex-app-info-${TEST_ID}.xml"
run_adb_capture 'app_info_ui_dump' yes "$OUTPUT/app_info_ui_dump.txt" shell uiautomator dump "$DEVICE_UI_DUMP"
run_adb_capture 'app_info_ui_readback' yes "$OUTPUT/app_info_ui.xml" shell cat "$DEVICE_UI_DUMP"
run_adb_capture 'app_info_ui_cleanup' yes "$OUTPUT/app_info_ui_cleanup.txt" shell rm "$DEVICE_UI_DUMP"
tap_status='not_run'
if [ "$TAP_HOME_ROW" -eq 1 ]; then
  run_adb_capture 'tap_home_row' yes "$OUTPUT/tap_home_row.txt" shell input tap "$TAP_X" "$TAP_Y"
  tap_status="$LAST_STATUS"
  sleep "$DURATION"
  capture_snapshot after_home_row_tap
  AFTER_TAP_UI_DUMP="/sdcard/codex-app-info-${TEST_ID}-after-tap.xml"
  run_adb_capture 'after_tap_ui_dump' yes "$OUTPUT/after_tap_ui_dump.txt" shell uiautomator dump "$AFTER_TAP_UI_DUMP"
  run_adb_capture 'after_tap_ui_readback' yes "$OUTPUT/after_tap_ui.xml" shell cat "$AFTER_TAP_UI_DUMP"
  run_adb_capture 'after_tap_ui_cleanup' yes "$OUTPUT/after_tap_ui_cleanup.txt" shell rm "$AFTER_TAP_UI_DUMP"
fi
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
  rg -n 'mResumedActivity|ResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|realActivity|origActivity|default_home|Home app|ホームアプリ|DefaultHome|Resolver|com\.android\.settings|com\.amazon\.firelauncher' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
else
  grep -REn 'mResumedActivity|ResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|realActivity|origActivity|default_home|Home app|ホームアプリ|DefaultHome|Resolver|com\.android\.settings|com\.amazon\.firelauncher' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
fi

printf 'open_app_info_status=%s\ntap_home_row=%s\ntap_home_row_status=%s\nrestore_home_status=%s\nfinished_utc=%s\n' \
  "$open_status" "$TAP_HOME_ROW" "$tap_status" "$restore_status" "$(timestamp_utc)" >> "$OUTPUT/test_metadata.txt"

{
  printf '# Launcher App info Settings probe summary\n\n'
  printf -- '- Test ID: `%s`\n' "$TEST_ID"
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- Package: `%s`\n' "$PACKAGE"
  printf -- '- App info open status: `%s`\n' "$open_status"
  printf -- '- Home-app row tap requested: `%s`\n' "$TAP_HOME_ROW"
  printf -- '- Home-app row tap status: `%s`\n' "$tap_status"
  printf -- '- Restore Home status: `%s`\n' "$restore_status"
  printf -- '- Finding status: `Hypothesis` until activity/UI outputs are reviewed.\n\n'
  printf '## Evidence\n\n'
  printf -- '- [Command manifest](command_manifest.tsv)\n'
  printf -- '- [App info UI dump](app_info_ui.xml)\n'
  printf -- '- [State focus lines](state_focus_lines.txt)\n'
  printf -- '- [Focused logcat](logcat_focus.txt)\n'
  printf -- '- [SHA-256 manifest](sha256sums.txt)\n\n'
  if [ "$TAP_HOME_ROW" -eq 1 ]; then
    printf 'The probe tapped only the visible Home-app row and recorded the resulting screen; it did not select a launcher or write the default.\n'
  else
    printf 'The probe did not click the Home-app preference; it only opened App info and restored Home.\n'
  fi
} > "$OUTPUT/test_summary.md"

write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"
printf 'Launcher App info probe completed: %s\n' "$TEST_ID"
if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'Launcher App info probe completed with %s required command failure(s); inspect %s\n' "$HARD_FAILURES" "$MANIFEST" >&2
  exit 2
fi
