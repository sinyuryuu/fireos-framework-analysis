#!/usr/bin/env bash
# Run one controlled preferred-HOME mutation using one existing test APK.
# Fire Launcher is never disabled, hidden, suspended, force-stopped, or
# cleared. The experiment installs a test package, writes ordinary preferred
# HOME state, probes both HOME entry paths, optionally reboots once, then
# restores Fire Launcher and removes only the test package.

set -Eeuo pipefail

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
CAPTURE="$ROOT/tools/scripts/capture_phase3c_state.sh"
RESTORE="$ROOT/tools/scripts/restore_phase3c_state.sh"

SERIAL=""
TEST_ID=""
APK=""
OUTPUT=""
DO_REBOOT=0
DO_LOCK_UNLOCK=0
DRY_RUN=0
APPROVE=0
RESTORE_ATTEMPTED=0

FIRE_COMPONENT="com.amazon.firelauncher/.Launcher"
TEST_PACKAGE="org.fireosresearch.home.p0"
TEST_COMPONENT="$TEST_PACKAGE/org.fireosresearch.home.HomeActivity"

usage() {
  cat <<'EOF'
Usage:
  run_phase3c_preferred_experiment.sh --serial SERIAL --test-id ID
      --apk TEST_APK --output DIR [--reboot] [--lock-unlock]
      [--approve-state-change] [--dry-run]

The live command requires the exact phrase:
  APPROVE PHASE3C-PREFERRED TEST-ID

Only one test package is accepted. Existing installation is refused.
EOF
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --test-id) [ "$#" -ge 2 ] || die '--test-id requires a value'; TEST_ID="$2"; shift 2 ;;
    --apk) [ "$#" -ge 2 ] || die '--apk requires a value'; APK="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --reboot) DO_REBOOT=1; shift ;;
    --lock-unlock) DO_LOCK_UNLOCK=1; shift ;;
    --approve-state-change) APPROVE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$APK" ] || die '--apk is required'
[ -n "$OUTPUT" ] || die '--output is required'
[ -f "$APK" ] || die "APK does not exist: $APK"
case "$OUTPUT" in /|.|..|"") die "refusing unsafe output directory: $OUTPUT" ;; esac
[ ! -e "$OUTPUT" ] || die "output directory already exists: $OUTPUT"

plan() {
  printf 'preferred\t0\t%s\n' "$FIRE_COMPONENT"
  printf 'package_state\t0\t%s\tABSENT\n' "$TEST_PACKAGE"
}

print_plan() {
  printf 'DRY-RUN: no state-changing command will execute.\n'
  printf 'DRY-RUN: serial=%s test-id=%s apk=%s output=%s\n' "$SERIAL" "$TEST_ID" "$APK" "$OUTPUT"
  printf 'DRY-RUN: install test APK: adb -s %s install --user 0 %s\n' "$SERIAL" "$APK"
  printf 'DRY-RUN: set preferred HOME: adb -s %s shell cmd package set-home-activity --user 0 %s\n' "$SERIAL" "$TEST_COMPONENT"
  printf 'DRY-RUN: HOME key: adb -s %s shell input keyevent 3\n' "$SERIAL"
  printf 'DRY-RUN: explicit HOME: adb -s %s shell am start -a android.intent.action.MAIN -c android.intent.category.HOME\n' "$SERIAL"
  [ "$DO_LOCK_UNLOCK" -eq 1 ] && printf 'DRY-RUN: lock/unlock probe: input keyevent 26 twice\n'
  [ "$DO_REBOOT" -eq 1 ] && printf 'DRY-RUN: one normal adb reboot with before/after snapshots\n'
  printf 'DRY-RUN: restore plan:\n'
  plan
}

if [ "$DRY_RUN" -eq 1 ]; then
  print_plan
  exit 0
fi

[ "$APPROVE" -eq 1 ] || die 'live experiment requires --approve-state-change'
printf 'This installs/removes only the research APK and writes ordinary preferred HOME state.\n'
printf 'Type APPROVE PHASE3C-PREFERRED %s to continue: ' "$TEST_ID"
read -r approval
[ "$approval" = "APPROVE PHASE3C-PREFERRED $TEST_ID" ] || die 'approval phrase did not match'

mkdir -p "$OUTPUT/mutations" "$OUTPUT/logs"
printf 'test_id=%s\nserial=%s\napk=%s\ntarget=%s\nrestore=%s\nreboot=%s\nlock_unlock=%s\nstarted_utc=%s\n' \
  "$TEST_ID" "$SERIAL" "$APK" "$TEST_COMPONENT" "$FIRE_COMPONENT" "$DO_REBOOT" "$DO_LOCK_UNLOCK" \
  "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.tsv"
plan > "$OUTPUT/restore.plan.tsv"

run_mutation() {
  local label="$1"
  shift
  set +e
  "$@" > "$OUTPUT/mutations/$label.stdout.txt" 2> "$OUTPUT/mutations/$label.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/mutations/$label.exit_code.txt"
  return "$status"
}

prepare_logcat() {
  local label="$1"
  run_mutation "logcat_clear_$label" adb -s "$SERIAL" logcat -c
}

capture_logcat() {
  local label="$1" status
  set +e
  adb -s "$SERIAL" logcat -b all -v threadtime -d \
    > "$OUTPUT/logs/$label.logcat.txt" \
    2> "$OUTPUT/logs/$label.logcat.stderr.txt"
  status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/logs/$label.logcat.exit_code.txt"
}

capture() {
  local name="$1"
  "$CAPTURE" --serial "$SERIAL" --test-id "$TEST_ID-$name" --output "$OUTPUT/$name"
}

wait_ready() {
  local i state boot
  for i in $(seq 1 90); do
    state=$(adb -s "$SERIAL" get-state 2>/dev/null || true)
    boot=$(adb -s "$SERIAL" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)
    [ "$state" = device ] && [ "$boot" = 1 ] && return 0
    sleep 1
  done
  die 'ADB/device did not return to boot_completed=1 within 90 seconds'
}

validate_device() {
  local state existing
  state=$(adb -s "$SERIAL" get-state 2>/dev/null || true)
  [ "$state" = device ] || die "device is not ready: $state"
  existing=$(adb -s "$SERIAL" shell pm path "$TEST_PACKAGE" 2>/dev/null || true)
  [ -z "$existing" ] || die "$TEST_PACKAGE is already installed; refusing to overwrite it"
}

cleanup_if_needed() {
  local status=$?
  trap - EXIT
  if [ "$RESTORE_ATTEMPTED" -eq 0 ] && [ "$(adb -s "$SERIAL" get-state 2>/dev/null || true)" = device ]; then
    RESTORE_ATTEMPTED=1
    set +e
    adb -s "$SERIAL" shell cmd package set-home-activity --user 0 "$FIRE_COMPONENT" \
      > "$OUTPUT/mutations/emergency_restore_preferred.stdout.txt" 2> "$OUTPUT/mutations/emergency_restore_preferred.stderr.txt"
    printf '%s\n' "$?" > "$OUTPUT/mutations/emergency_restore_preferred.exit_code.txt"
    adb -s "$SERIAL" shell pm uninstall --user 0 "$TEST_PACKAGE" \
      > "$OUTPUT/mutations/emergency_uninstall.stdout.txt" 2> "$OUTPUT/mutations/emergency_uninstall.stderr.txt"
    printf '%s\n' "$?" > "$OUTPUT/mutations/emergency_uninstall.exit_code.txt"
    set -e
  fi
  exit "$status"
}
trap cleanup_if_needed EXIT

validate_device
capture before

run_mutation install_test adb -s "$SERIAL" install --user 0 "$APK"
capture_logcat install
capture after_install

prepare_logcat set_preferred
run_mutation set_preferred adb -s "$SERIAL" shell cmd package set-home-activity --user 0 "$TEST_COMPONENT"
sleep 1
capture_logcat set_preferred
capture after_preferred

run_mutation prepare_settings adb -s "$SERIAL" shell am start -n com.android.settings/.Settings
sleep 2
prepare_logcat home_key
run_mutation home_key adb -s "$SERIAL" shell input keyevent 3
sleep 2
capture_logcat home_key
capture after_home_key

run_mutation prepare_settings_explicit adb -s "$SERIAL" shell am start -n com.android.settings/.Settings
sleep 2
prepare_logcat explicit_home
run_mutation explicit_home adb -s "$SERIAL" shell am start -a android.intent.action.MAIN -c android.intent.category.HOME
sleep 2
capture_logcat explicit_home
capture after_explicit_home

if [ "$DO_LOCK_UNLOCK" -eq 1 ]; then
  prepare_logcat lock_unlock
  run_mutation lock_screen adb -s "$SERIAL" shell input keyevent 26
  sleep 2
  run_mutation unlock_screen adb -s "$SERIAL" shell input keyevent 26
  sleep 3
  capture_logcat lock_unlock
  capture after_lock_unlock
fi

if [ "$DO_REBOOT" -eq 1 ]; then
  prepare_logcat reboot
  capture_logcat pre_reboot
  capture before_reboot
  run_mutation reboot adb -s "$SERIAL" reboot
  wait_ready
  capture_logcat after_reboot
  capture after_reboot
fi

RESTORE_ATTEMPTED=1
prepare_logcat restore
set +e
printf 'APPROVE PHASE3C-RESTORE %s\n' "$TEST_ID" | \
  "$RESTORE" --serial "$SERIAL" --test-id "$TEST_ID" --plan "$OUTPUT/restore.plan.tsv" --approve-state-change \
  > "$OUTPUT/mutations/restore.stdout.txt" 2> "$OUTPUT/mutations/restore.stderr.txt"
restore_status=$?
set -e
printf '%s\n' "$restore_status" > "$OUTPUT/mutations/restore.exit_code.txt"
[ "$restore_status" -eq 0 ] || die 'explicit restore failed; inspect restore evidence'
sleep 1
capture_logcat restore
capture after_rollback_pre_uninstall

prepare_logcat uninstall_test
run_mutation uninstall_test adb -s "$SERIAL" shell pm uninstall --user 0 "$TEST_PACKAGE"
sleep 1
capture_logcat uninstall_test
capture after_rollback

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
{
  printf '# Phase 3C preferred HOME experiment\n\n'
  printf '%s\n' "- Test ID: $TEST_ID" "- Serial: $SERIAL" "- Test package: $TEST_PACKAGE"
  printf '%s\n' "- Test component: $TEST_COMPONENT" "- Restore component: $FIRE_COMPONENT"
  printf '%s\n' "- Reboot requested: $DO_REBOOT" "- Lock/unlock requested: $DO_LOCK_UNLOCK"
  printf '%s\n' '- The runner never disabled, hid, suspended, force-stopped, or cleared Fire Launcher.'
  printf '%s\n' '- Review resolver, preferred dump, foreground state, and rollback snapshots before assigning causality.'
  printf '%s\n' '- SHA-256 manifest: sha256sums.txt'
} > "$OUTPUT/result.md"
find "$OUTPUT" -type f ! -name 'sha256sums*.txt' -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums-final.txt"

trap - EXIT
printf 'Phase 3C preferred experiment completed: %s\n' "$TEST_ID"
