#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
CAPTURE="$SCRIPT_DIR/capture_phase3c_state.sh"
SERIAL=""
TEST_ID=""
REDIRECT_APK=""
ALIAS_APK=""
OUTPUT=""
PHASE=""
ITERATIONS=30
APPROVE=0
APPROVAL_VALUE=""
MANUAL_VALUE=""

REDIRECT_PACKAGE="org.fireosresearch.phase4.redirect"
REDIRECT_SERVICE="org.fireosresearch.phase4.redirect/org.fireosresearch.phase4.redirect.LauncherRedirectService"
REDIRECT_ACTIVITY="$REDIRECT_PACKAGE/.ControlActivity"
ALIAS_PACKAGE="org.fireosresearch.phase4.alias"
# HomeActivity is declared in the test manifest and is also a harmless
# foreground probe. ProbeActivity is source-only and intentionally not an
# exported/declared component.
ALIAS_PROBE="$ALIAS_PACKAGE/.HomeActivity"
FIRE_PACKAGE="com.amazon.firelauncher"

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }
sha256_file() { shasum -a 256 "$1" | awk '{print $1}'; }

usage() {
  cat <<'EOF'
Usage:
  run_phase4_accessibility_experiment.sh --phase prepare|measure|rollback
      --serial SERIAL --test-id ID --redirect-apk APK --alias-apk APK
      --output DIR [--iterations N] [--approve-state-change]
      [--approval-phrase VALUE] [--manual-consent-confirmed VALUE]

prepare installs only the two research APKs, captures a before snapshot,
opens the visible ControlActivity and Android Accessibility Settings, and
stops for the device owner to toggle the app and service manually.

measure requires the device owner to have manually enabled the service and
the visible redirect toggle. It only starts the test ProbeActivity and sends
KEYCODE_HOME; it never writes Settings and never changes Fire Launcher state.

rollback requires the device owner to disable the service in Settings first.
It then removes only the two research APKs and verifies Fire resolver state.

Approval phrases:
  APPROVE PHASE4-ACCESSIBILITY-TEST-ID
  CONFIRM MANUAL ACCESSIBILITY CONSENT FOR TEST-ID
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --phase) [ "$#" -ge 2 ] || die '--phase requires a value'; PHASE="$2"; shift 2 ;;
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --test-id) [ "$#" -ge 2 ] || die '--test-id requires a value'; TEST_ID="$2"; shift 2 ;;
    --redirect-apk) [ "$#" -ge 2 ] || die '--redirect-apk requires a value'; REDIRECT_APK="$2"; shift 2 ;;
    --alias-apk) [ "$#" -ge 2 ] || die '--alias-apk requires a value'; ALIAS_APK="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --iterations) [ "$#" -ge 2 ] || die '--iterations requires a value'; ITERATIONS="$2"; shift 2 ;;
    --approve-state-change) APPROVE=1; shift ;;
    --approval-phrase) [ "$#" -ge 2 ] || die '--approval-phrase requires a value'; APPROVAL_VALUE="$2"; shift 2 ;;
    --manual-consent-confirmed) [ "$#" -ge 2 ] || die '--manual-consent-confirmed requires a value'; MANUAL_VALUE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ "$PHASE" = prepare ] || [ "$PHASE" = measure ] || [ "$PHASE" = rollback ] || die '--phase must be prepare, measure, or rollback'
[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$OUTPUT" ] || die '--output is required'
[ "$OUTPUT" != "/" ] && [ "$OUTPUT" != "." ] && [ "$OUTPUT" != ".." ] || die 'unsafe output directory'
[ -x "$CAPTURE" ] || die "capture script is not executable: $CAPTURE"

if [ "$PHASE" = prepare ] || [ "$PHASE" = measure ]; then
  [ -f "$REDIRECT_APK" ] || die "redirect APK not found: $REDIRECT_APK"
  [ -f "$ALIAS_APK" ] || die "alias APK not found: $ALIAS_APK"
  case "$REDIRECT_APK $ALIAS_APK" in
    *com.amazon.firelauncher*) die 'Fire package name appeared in APK argument' ;;
  esac
fi

ADB=(adb -s "$SERIAL")
run_capture() {
  local name="$1"; shift
  printf '%s\n' "adb -s $SERIAL $*" > "$OUTPUT/$name.command.txt"
  set +e
  "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
  return "$status"
}

ensure_device() {
  local devices
  devices=$("${ADB[@]}" get-state 2>/dev/null || true)
  [ "$devices" = device ] || die "serial is not in device state: $devices"
}

check_for_forbidden_fire_mutation() {
  local command_text="$*"
  case "$command_text" in
    *com.amazon.firelauncher*) die "Fire package appeared in mutation command: $command_text" ;;
  esac
}

require_approval() {
  [ "$APPROVE" -eq 1 ] || die 'live phase requires --approve-state-change'
  local expected="APPROVE PHASE4-$TEST_ID"
  local value="$APPROVAL_VALUE"
  if [ -z "$value" ]; then
    printf 'This installs/removes only the two research APKs. Type %s to continue: ' "$expected"
    read -r value
  fi
  [ "$value" = "$expected" ] || die 'approval phrase did not match'
}

require_manual_consent() {
  local expected="CONFIRM MANUAL ACCESSIBILITY CONSENT FOR $TEST_ID"
  [ "$MANUAL_VALUE" = "$expected" ] || die "manual-consent confirmation must be: $expected"
  local accessibility
  accessibility=$("${ADB[@]}" shell dumpsys accessibility 2>/dev/null || true)
  printf '%s\n' "$accessibility" > "$OUTPUT/accessibility-before-measure.stdout.txt"
  printf '%s\n' "adb -s $SERIAL shell dumpsys accessibility" > "$OUTPUT/accessibility-before-measure.command.txt"
  if ! printf '%s\n' "$accessibility" | grep -Eiq 'Phase 4 redirect control|org\.fireosresearch\.phase4\.redirect'; then
    die 'redirect service is not visibly enabled in dumpsys accessibility; no measurement executed'
  fi
}

if [ "$PHASE" = prepare ]; then
  require_approval
  [ ! -e "$OUTPUT" ] || die "refusing to overwrite existing output: $OUTPUT"
  mkdir -p "$OUTPUT"
  ensure_device
  redirect_path=$("${ADB[@]}" shell pm path "$REDIRECT_PACKAGE" 2>/dev/null || true)
  if [ -n "$redirect_path" ]; then
    die 'redirect package is already installed'
  fi
  alias_path=$("${ADB[@]}" shell pm path "$ALIAS_PACKAGE" 2>/dev/null || true)
  if [ -n "$alias_path" ]; then
    die 'alias package is already installed'
  fi
  cat > "$OUTPUT/metadata.tsv" <<EOF
test_id\t$TEST_ID
serial\t$SERIAL
redirect_package\t$REDIRECT_PACKAGE
redirect_service\t$REDIRECT_SERVICE
alias_package\t$ALIAS_PACKAGE
fire_package_guard\t$FIRE_PACKAGE
redirect_apk\t$REDIRECT_APK
redirect_apk_sha256\t$(sha256_file "$REDIRECT_APK")
alias_apk\t$ALIAS_APK
alias_apk_sha256\t$(sha256_file "$ALIAS_APK")
mutation_scope\tinstall/remove research APKs only; manual Accessibility consent
forbidden\tFire Launcher mutation; settings put; unknown Binder; reboot
timestamp_utc\t$(date -u '+%Y-%m-%dT%H:%M:%SZ')
EOF
  "$CAPTURE" --serial "$SERIAL" --test-id "$TEST_ID-BEFORE" --output "$OUTPUT/before" > "$OUTPUT/before-capture.stdout.txt" 2> "$OUTPUT/before-capture.stderr.txt"
  run_capture install_redirect "${ADB[@]}" install --user 0 "$REDIRECT_APK"
  run_capture install_alias "${ADB[@]}" install --user 0 "$ALIAS_APK"
  run_capture installed_redirect_path "${ADB[@]}" shell pm path "$REDIRECT_PACKAGE"
  run_capture installed_alias_path "${ADB[@]}" shell pm path "$ALIAS_PACKAGE"
  run_capture accessibility_after_install "${ADB[@]}" shell dumpsys accessibility
  run_capture open_control "${ADB[@]}" shell am start -W -n "$REDIRECT_ACTIVITY"
  run_capture open_accessibility_settings "${ADB[@]}" shell am start -a android.settings.ACCESSIBILITY_SETTINGS
  cat > "$OUTPUT/next-step.md" <<EOF
# Manual consent required

1. In the visible ControlActivity, turn on **Redirect enabled**.
2. In Android Settings, manually enable the Phase 4 redirect Accessibility service.
3. Leave the service enabled and return to the test app.
4. Run the documented measure command with the exact manual-consent phrase.

No shell command in this preparation phase enabled Accessibility or changed a
Settings provider value.
EOF
  find "$OUTPUT" -type f ! -name sha256sums-preparation.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums-preparation.txt"
  printf 'Preparation complete; manual consent is required before measurement: %s\n' "$OUTPUT"
  exit 0
fi

[ -d "$OUTPUT" ] || die "output directory not found: $OUTPUT"
ensure_device

if [ "$PHASE" = measure ]; then
  require_manual_consent
  case "$ITERATIONS" in ''|*[!0-9]*) die '--iterations must be a non-negative integer' ;; esac
  [ "$ITERATIONS" -gt 0 ] || die '--iterations must be greater than zero'
  mkdir -p "$OUTPUT/measure"
  run_capture logcat_clear_before_measure "${ADB[@]}" shell logcat -c
  run_capture resolve_before_measure "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
  for i in $(seq 1 "$ITERATIONS"); do
    run_capture "measure/launch_probe_${i}" "${ADB[@]}" shell am start -W -n "$ALIAS_PROBE" || true
    sleep 0.25
    run_capture "measure/home_key_${i}" "${ADB[@]}" shell input keyevent 3
    sleep 1.5
    run_capture "measure/foreground_${i}" "${ADB[@]}" shell dumpsys activity activities
    run_capture "measure/window_${i}" "${ADB[@]}" shell dumpsys window windows
  done
  run_capture logcat_after_measure "${ADB[@]}" shell logcat -d -b all -v threadtime
  run_capture accessibility_after_measure "${ADB[@]}" shell dumpsys accessibility
  run_capture resolve_after_measure "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
  {
    printf 'iteration\tresumed_or_focus\talias_observed\n'
    for i in $(seq 1 "$ITERATIONS"); do
      line=$(grep -E 'mResumedActivity|mFocusedApp' "$OUTPUT/measure/foreground_${i}.stdout.txt" | head -1 | tr '\\t' ' ' || true)
      if printf '%s\n' "$line" | grep -Fq "$ALIAS_PACKAGE"; then observed=yes; else observed=no; fi
      printf '%s\t%s\t%s\n' "$i" "$line" "$observed"
    done
  } > "$OUTPUT/measure/summary.tsv"
  cat > "$OUTPUT/measure/result.md" <<EOF
# $TEST_ID measurement

- Iterations: $ITERATIONS
- Input: KEYCODE_HOME after each launch of the test probe.
- Fire Launcher was not stopped, disabled, hidden, suspended, uninstalled, or cleared.
- No Settings provider write and no unknown Binder call was executed.
- measure/summary.tsv records whether the alias package was observed in the foreground dump.
- This is a foreground redirect measurement, not a HOME resolver replacement measurement.

Before rollback, manually disable the redirect service in Android Settings and
turn off the visible toggle. Then run the documented rollback command.
EOF
  find "$OUTPUT" -type f ! -name sha256sums-measurement.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums-measurement.txt"
  printf 'Measurement complete; manual service disable is required before rollback: %s\n' "$OUTPUT"
  exit 0
fi

require_approval
local_accessibility=$("${ADB[@]}" shell dumpsys accessibility 2>/dev/null || true)
printf '%s\n' "$local_accessibility" > "$OUTPUT/accessibility-before-rollback.stdout.txt"
printf '%s\n' "adb -s $SERIAL shell dumpsys accessibility" > "$OUTPUT/accessibility-before-rollback.command.txt"
if printf '%s\n' "$local_accessibility" | grep -Eiq 'Phase 4 redirect control|org\.fireosresearch\.phase4\.redirect'; then
  die 'redirect service still appears enabled; disable it manually in Settings before rollback'
fi
run_capture uninstall_redirect "${ADB[@]}" shell pm uninstall --user 0 "$REDIRECT_PACKAGE"
run_capture uninstall_alias "${ADB[@]}" shell pm uninstall --user 0 "$ALIAS_PACKAGE"
run_capture after_redirect_path "${ADB[@]}" shell pm path "$REDIRECT_PACKAGE" || true
run_capture after_alias_path "${ADB[@]}" shell pm path "$ALIAS_PACKAGE" || true
run_capture after_resolve "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_capture after_foreground "${ADB[@]}" shell dumpsys activity activities
run_capture after_devices "${ADB[@]}" get-state
"$CAPTURE" --serial "$SERIAL" --test-id "$TEST_ID-AFTER-ROLLBACK" --output "$OUTPUT/after_rollback" > "$OUTPUT/after-capture.stdout.txt" 2> "$OUTPUT/after-capture.stderr.txt"
if grep -q "$REDIRECT_PACKAGE\|$ALIAS_PACKAGE" "$OUTPUT/after_redirect_path.stdout.txt" "$OUTPUT/after_alias_path.stdout.txt"; then
  die 'rollback failed: research package still has an installed path'
fi
if ! grep -Fq "$FIRE_PACKAGE" "$OUTPUT/after_resolve.stdout.txt"; then
  die 'rollback verification did not observe Fire Launcher resolver'
fi
if [ "$(cat "$OUTPUT/after_devices.stdout.txt")" != device ]; then
  die 'rollback verification did not observe adb device state'
fi
cat > "$OUTPUT/rollback-result.md" <<EOF
# $TEST_ID rollback

- Manual Accessibility disable was verified by dumpsys accessibility before package removal.
- Only $REDIRECT_PACKAGE and $ALIAS_PACKAGE were removed.
- Fire Launcher package state and data were not targeted.
- Final resolver included $FIRE_PACKAGE.
- ADB remained in device state.
- Before/after state and hashes are preserved in this directory.
EOF
find "$OUTPUT" -type f ! -name sha256sums-final.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums-final.txt"
printf 'Accessibility experiment rolled back successfully: %s\n' "$OUTPUT"
