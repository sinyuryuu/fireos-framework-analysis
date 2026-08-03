#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
CAPTURE="$SCRIPT_DIR/capture_phase3c_state.sh"
SERIAL=""
TEST_ID=""
APK=""
OUTPUT=""
DRY_RUN=0
APPROVE=0
APPROVAL_VALUE=""
TEST_PACKAGE="org.fireosresearch.phase4.alias"
FIRE_PACKAGE="com.amazon.firelauncher"

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }
sha256_file() { shasum -a 256 "$1" | awk '{print $1}'; }
usage() {
  cat <<'EOF'
Usage:
  run_phase4_alias_experiment.sh --serial SERIAL --test-id ID --apk APK
      --output DIR [--approve-state-change] [--dry-run]

The live operation installs and removes only org.fireosresearch.phase4.alias.
It refuses to mutate, stop, or clear com.amazon.firelauncher and never calls
set-home-activity.  Approval phrase:
  APPROVE PHASE4-ALIAS-TEST-ID
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --test-id) [ "$#" -ge 2 ] || die '--test-id requires a value'; TEST_ID="$2"; shift 2 ;;
    --apk) [ "$#" -ge 2 ] || die '--apk requires a value'; APK="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --approve-state-change) APPROVE=1; shift ;;
    --approval-phrase) [ "$#" -ge 2 ] || die '--approval-phrase requires a value'; APPROVAL_VALUE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$APK" ] || die '--apk is required'
[ -n "$OUTPUT" ] || die '--output is required'
[ -f "$APK" ] || die "APK not found: $APK"
[ -x "$CAPTURE" ] || die "capture script is not executable: $CAPTURE"
[ "$OUTPUT" != "/" ] && [ "$OUTPUT" != "." ] && [ "$OUTPUT" != ".." ] || die 'unsafe output directory'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no ADB command and no output directory will be created.\n'
  printf 'DRY-RUN: serial=%s test-id=%s apk=%s output=%s\n' "$SERIAL" "$TEST_ID" "$APK" "$OUTPUT"
  printf 'DRY-RUN: read-only before/after capture; install APK; explicit-start test components; Home key; uninstall APK.\n'
  printf 'DRY-RUN: forbidden target=%s; no set-home-activity; no Fire package state mutation.\n' "$FIRE_PACKAGE"
  exit 0
fi

[ ! -e "$OUTPUT" ] || die "refusing to overwrite existing output: $OUTPUT"
[ "$APPROVE" -eq 1 ] || die 'live experiment requires --approve-state-change'
mkdir -p "$OUTPUT"
ADB=(adb -s "$SERIAL")

devices="$OUTPUT/devices-before.stdout.txt"
set +e
"${ADB[@]}" devices -l > "$devices" 2> "$OUTPUT/devices-before.stderr.txt"
devices_status=$?
set -e
printf '%s\n' "$devices_status" > "$OUTPUT/devices-before.exit_code.txt"
[ "$devices_status" -eq 0 ] || die 'adb devices failed'
awk -v serial="$SERIAL" '$1 == serial && $2 == "device" { found=1 } END { exit(found ? 0 : 1) }' "$devices" || die 'serial is not connected as device'

before_path=$(${ADB[@]} shell pm path "$TEST_PACKAGE" 2>/dev/null || true)
[ -z "$before_path" ] || die "test package is already installed: $before_path"

cat > "$OUTPUT/metadata.tsv" <<EOF
test_id	$TEST_ID
serial	$SERIAL
test_package	$TEST_PACKAGE
fire_package_guard	$FIRE_PACKAGE
apk	$APK
apk_sha256	$(sha256_file "$APK")
timestamp_utc	$(date -u '+%Y-%m-%dT%H:%M:%SZ')
mutation_scope	install/remove test APK only
forbidden	Fire Launcher state mutation, set-home-activity, settings, reboot
EOF

"$CAPTURE" --serial "$SERIAL" --test-id "$TEST_ID-BEFORE" --output "$OUTPUT/before" > "$OUTPUT/before-capture.stdout.txt" 2> "$OUTPUT/before-capture.stderr.txt"

run_cmd() {
  local name="$1"; shift
  case "$*" in *com.amazon.firelauncher*) die "Fire package appeared in live mutation command: $*" ;; esac
  printf '%s\n' "adb -s $SERIAL $*" > "$OUTPUT/$name.command.txt"
  set +e
  "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
  return "$status"
}

approval="APPROVE PHASE4-$TEST_ID"
if [ -n "$APPROVAL_VALUE" ]; then
  typed="$APPROVAL_VALUE"
else
  printf 'This installs/removes only %s. Type %s to continue: ' "$TEST_PACKAGE" "$approval"
  read -r typed
fi
[ "$typed" = "$approval" ] || die 'approval phrase did not match; no install was executed'

run_cmd install_test "${ADB[@]}" install --user 0 "$APK"
run_cmd installed_path "${ADB[@]}" shell pm path "$TEST_PACKAGE"
run_cmd installed_package_dump "${ADB[@]}" shell dumpsys package "$TEST_PACKAGE"
run_cmd installed_home_query "${ADB[@]}" shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_cmd installed_home_resolve "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_cmd installed_home_query_pm "${ADB[@]}" shell pm query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_cmd logcat_clear "${ADB[@]}" shell logcat -c

for component in \
  "$TEST_PACKAGE/.HomeActivity" \
  "$TEST_PACKAGE/.HomeAliasDefault" \
  "$TEST_PACKAGE/.HomeAliasHomeOnly" \
  "$TEST_PACKAGE/.DirectBootHomeActivity" \
  "$TEST_PACKAGE/.SpecificHomeActivity" \
  "$TEST_PACKAGE/.SecondaryHomeActivity"; do
  safe=${component##*/}
  safe=${safe//\$/_}
  run_cmd "explicit_${safe}" "${ADB[@]}" shell am start -W -n "$component" || true
done
run_cmd implicit_home "${ADB[@]}" shell am start -W -a android.intent.action.MAIN -c android.intent.category.HOME || true
run_cmd home_key "${ADB[@]}" shell input keyevent 3
run_cmd logcat_after_events "${ADB[@]}" shell logcat -d -b all -v threadtime
run_cmd foreground_after_events "${ADB[@]}" shell dumpsys activity activities
run_cmd window_after_events "${ADB[@]}" shell dumpsys window windows

run_cmd uninstall_test "${ADB[@]}" shell pm uninstall --user 0 "$TEST_PACKAGE"
run_cmd after_path "${ADB[@]}" shell pm path "$TEST_PACKAGE" || true
run_cmd after_resolve "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_cmd after_foreground "${ADB[@]}" shell dumpsys activity activities
"$CAPTURE" --serial "$SERIAL" --test-id "$TEST_ID-AFTER-ROLLBACK" --output "$OUTPUT/after_rollback" > "$OUTPUT/after-capture.stdout.txt" 2> "$OUTPUT/after-capture.stderr.txt"

if grep -q "$TEST_PACKAGE" "$OUTPUT/after_path.stdout.txt"; then
  die "rollback failed: test package still has a path"
fi
if grep -q "$TEST_PACKAGE" "$OUTPUT/after_resolve.stdout.txt"; then
  die "rollback failed: test package resolved as HOME"
fi
if ! grep -q "$FIRE_PACKAGE" "$OUTPUT/after_resolve.stdout.txt"; then
  die "rollback verification did not observe Fire Launcher resolver"
fi

cat > "$OUTPUT/result.md" <<EOF
# $TEST_ID result

- Installed and removed only \`$TEST_PACKAGE\`.
- No \`set-home-activity\`, settings, Fire Launcher state mutation, or reboot was executed.
- HOME candidate, explicit component, implicit HOME, Home key, and rollback outputs are preserved.
- Final resolver included \`$FIRE_PACKAGE\`; test package path was absent after rollback.
- SHA-256 manifest: \`sha256sums.txt\`.
EOF
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Phase 4 alias experiment completed and rolled back: %s\n' "$OUTPUT"
