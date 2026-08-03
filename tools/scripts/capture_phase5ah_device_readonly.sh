#!/usr/bin/env bash
# Bounded exact-target read-only capture for Phase 5AH.
# Never writes to the device, opens a device node, reads a block device, or
# starts a payload. The output directory is host-side and must be new.
set -u
export LC_ALL=C

SERIAL=""
TEST_ID=""
OUTPUT=""
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --test-id) [ "$#" -ge 2 ] || die '--test-id requires a value'; TEST_ID="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) printf '%s\n' 'Usage: capture_phase5ah_device_readonly.sh --serial SERIAL --test-id TEST-ID --output DIR [--dry-run]'; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in /|.|..|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac

COMMAND_NAMES=(device_state identity props kernel_release selinux cmdline node_metadata home firelauncher_path)
if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no device command will run and no files will be written.\n'
  printf 'DRY-RUN: test_id=%s serial=%s output=%s\n' "$TEST_ID" "$SERIAL" "$OUTPUT"
  printf '%s\n' "${COMMAND_NAMES[@]}"
  exit 0
fi

command -v adb >/dev/null 2>&1 || die 'adb is required'
command -v shasum >/dev/null 2>&1 || die 'shasum is required'
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"

mkdir -p "$OUTPUT"
START_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
ADB=(adb -s "$SERIAL")
printf 'test_id\t%s\nserial\t%s\nstart_utc\t%s\nmode\tread-only\n' "$TEST_ID" "$SERIAL" "$START_UTC" > "$OUTPUT/metadata.tsv"

run_capture() {
  local name="$1"; shift
  printf '%q ' "$@" > "$OUTPUT/${name}.command.txt"
  printf '\n' >> "$OUTPUT/${name}.command.txt"
  "$@" > "$OUTPUT/${name}.stdout.txt" 2> "$OUTPUT/${name}.stderr.txt"
  printf '%s\n' "$?" > "$OUTPUT/${name}.exit_code.txt"
  printf '%s\t%s\n' "$name" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$OUTPUT/metadata.tsv"
  return 0
}

run_capture device_state "${ADB[@]}" get-state
run_capture identity "${ADB[@]}" shell id
run_capture props "${ADB[@]}" shell getprop
run_capture kernel_release "${ADB[@]}" shell uname -a
run_capture selinux "${ADB[@]}" shell getenforce
run_capture cmdline "${ADB[@]}" shell cat /proc/cmdline
run_capture node_metadata "${ADB[@]}" shell ls -lZ /dev/ion /dev/aed0 /dev/aed1 /dev/atf_log /dev/sspm
run_capture home "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
run_capture firelauncher_path "${ADB[@]}" shell pm path com.amazon.firelauncher

END_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'end_utc\t%s\n' "$END_UTC" >> "$OUTPUT/metadata.tsv"
printf '%s\n' \
  "Test ID: $TEST_ID" \
  "Serial: $SERIAL" \
  'All commands are read-only host captures.' \
  'No device node was opened; no block device was read; no package, setting, process, boot, or partition state was changed.' \
  > "$OUTPUT/commands.txt"
printf '# %s\n\n- Serial: %s\n- Start UTC: %s\n- End UTC: %s\n- Device writes: none\n- Device nodes opened: none\n- Block devices read: none\n- Payloads executed: none\n' "$TEST_ID" "$SERIAL" "$START_UTC" "$END_UTC" > "$OUTPUT/result.md"
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | while IFS= read -r -d '' file; do shasum -a 256 "$file"; done > "$OUTPUT/sha256sums.txt"
printf 'Captured read-only device state in %s\n' "$OUTPUT"
