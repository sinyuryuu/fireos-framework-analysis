#!/usr/bin/env bash

# Phase 3B HOME-path observation.  The only device mutations are logcat
# buffer clearing plus foreground HOME actions (am start/input keyevent).  It
# never changes package state, settings, overlays, policy, or partitions.

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
TEST_ID=''
OUTPUT=''
MODE=''
DURATION=5
APPROVED=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: capture_home_path_phase3b.sh --serial SERIAL --test-id ID
       --output DIR --mode explicit|keyevent [--duration SEC]
       --approve-state-change [--dry-run]

explicit: am start -a MAIN -c HOME
keyevent: input keyevent 3

The script preserves before/after resolver, activity, recents, window,
preferred, and full logcat output. It sends one final HOME keyevent to return
the foreground to the normal HOME path. No package/settings/policy mutation is
performed.
EOF
}

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || fail '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --test-id) [ "$#" -ge 2 ] || fail '--test-id requires a value'; TEST_ID="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || fail '--output requires a path'; OUTPUT="$2"; shift 2 ;;
    --mode) [ "$#" -ge 2 ] || fail '--mode requires explicit or keyevent'; MODE="$2"; shift 2 ;;
    --duration) [ "$#" -ge 2 ] || fail '--duration requires seconds'; DURATION="$2"; shift 2 ;;
    --approve-state-change) APPROVED=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) fail "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || fail '--serial is required'
[ -n "$TEST_ID" ] || fail '--test-id is required'
[ -n "$OUTPUT" ] || fail '--output is required'
case "$MODE" in explicit|keyevent) ;; *) fail '--mode must be explicit or keyevent' ;; esac
case "$DURATION" in ''|*[!0-9]*) fail '--duration must be a non-negative integer' ;; esac
[ "$APPROVED" -eq 1 ] || fail 'foreground action requires --approve-state-change'

ADB=(adb -s "$SERIAL")

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no ADB command or output directory will be created.\n'
  printf 'DRY-RUN: %s devices -l\n' "${ADB[*]}"
  printf 'DRY-RUN: %s shell logcat -b all -c\n' "${ADB[*]}"
  if [ "$MODE" = explicit ]; then
    printf 'DRY-RUN: %s shell am start -a android.intent.action.MAIN -c android.intent.category.HOME\n' "${ADB[*]}"
  else
    printf 'DRY-RUN: %s shell input keyevent 3\n' "${ADB[*]}"
  fi
  printf 'DRY-RUN: final %s shell input keyevent 3\n' "${ADB[*]}"
  exit 0
fi

validate_serial "$SERIAL"
ensure_new_path "$OUTPUT"
mkdir -p "$OUTPUT/before" "$OUTPUT/after"

printf 'field\tvalue\nphase\t3B\nserial\t%s\ntest_id\t%s\nmode\t%s\nduration\t%s\nstarted_utc\t%s\nstate_scope\tforeground_and_logcat_only\n' \
  "$SERIAL" "$TEST_ID" "$MODE" "$DURATION" "$(timestamp_utc)" > "$OUTPUT/metadata.tsv"

cat > "$OUTPUT/commands.txt" <<EOF
adb -s '$SERIAL' devices -l
adb -s '$SERIAL' shell logcat -b all -c
adb -s '$SERIAL' shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
adb -s '$SERIAL' shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
adb -s '$SERIAL' shell dumpsys package preferred-activities
adb -s '$SERIAL' shell dumpsys activity activities
adb -s '$SERIAL' shell dumpsys activity recents
adb -s '$SERIAL' shell dumpsys window windows
adb -s '$SERIAL' shell am start -a android.intent.action.MAIN -c android.intent.category.HOME
adb -s '$SERIAL' shell input keyevent 3
EOF

capture() {
  local label="$1"
  shift
  local status
  set +e
  "$@" > "$OUTPUT/$label.stdout.txt" 2> "$OUTPUT/$label.stderr.txt"
  status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$label.exit_code.txt"
}

capture devices_before "${ADB[@]}" devices -l
grep -Eq "^${SERIAL}[[:space:]].*device" "$OUTPUT/devices_before.stdout.txt" || fail 'serial is not in device state'
capture logcat_clear "${ADB[@]}" shell logcat -b all -c

snapshot() {
  local phase="$1"
  capture "before/$phase.home_resolve" "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
  capture "before/$phase.home_query" "${ADB[@]}" shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
  capture "before/$phase.preferred" "${ADB[@]}" shell dumpsys package preferred-activities
  capture "before/$phase.activity" "${ADB[@]}" shell dumpsys activity activities
  capture "before/$phase.recents" "${ADB[@]}" shell dumpsys activity recents
  capture "before/$phase.window" "${ADB[@]}" shell dumpsys window windows
}

snapshot initial

LOGCAT="$OUTPUT/logcat.txt"
"${ADB[@]}" logcat -b all -v threadtime > "$LOGCAT" 2> "$OUTPUT/logcat.stderr.txt" &
LOGCAT_PID=$!
cleanup_logcat() {
  kill "$LOGCAT_PID" 2>/dev/null || true
  wait "$LOGCAT_PID" 2>/dev/null || true
}
trap cleanup_logcat EXIT
sleep 1

if [ "$MODE" = explicit ]; then
  capture action_explicit_home "${ADB[@]}" shell am start -a android.intent.action.MAIN -c android.intent.category.HOME
else
  capture action_keyevent_home "${ADB[@]}" shell input keyevent 3
fi
sleep "$DURATION"
snapshot observed

# Restore the normal foreground HOME path. This is not a package or settings
# restore; it only makes the foreground state deterministic for handoff.
capture restore_home_keyevent "${ADB[@]}" shell input keyevent 3
sleep 2
snapshot final

cleanup_logcat
trap - EXIT

{
  printf '# Phase 3B HOME path observation\n\n'
  printf -- '- Test ID: `%s`\n' "$TEST_ID"
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- Mode: `%s`\n' "$MODE"
  printf '%s\n' '- Device mutations: logcat buffer clear and foreground HOME action only.'
  printf '%s\n' '- Package/settings/policy/overlay/partition writes: none.'
  printf '%s\n' '- Final foreground restoration: `input keyevent 3`.'
  printf '%s\n' '- Raw stdout/stderr, exit codes, dumps, and full logcat are preserved.'
} > "$OUTPUT/result.md"

write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"
printf 'Phase 3B HOME path capture completed: %s\n' "$TEST_ID"
