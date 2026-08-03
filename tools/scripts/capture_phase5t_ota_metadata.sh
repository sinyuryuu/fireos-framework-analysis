#!/usr/bin/env bash
# Read-only OTA/build metadata capture. Never starts an update, reboots, or
# writes Android/device state.
set -Eeuo pipefail

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
    -h|--help)
      printf '%s\n' 'Usage: capture_phase5t_ota_metadata.sh --serial SERIAL --test-id ID --output DIR [--dry-run]'
      exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$OUTPUT" ] || die '--output is required'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: verify adb -s %q get-state\n' "$SERIAL"
  printf '%s\n' 'DRY-RUN: collect getprop, OTA/cache listings, OTA package paths, and HOME result only'
  printf 'DRY-RUN: write raw outputs and SHA-256 manifest under %q\n' "$OUTPUT"
  exit 0
fi

case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"
mkdir -p "$OUTPUT"

ADB=(adb -s "$SERIAL")
STAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'test_id=%s\nserial=%s\ntimestamp_utc=%s\nread_only=true\n' \
  "$TEST_ID" "$SERIAL" "$STAMP" > "$OUTPUT/metadata.tsv"

run_local() {
  local name="$1"; shift
  printf '%q ' "$@" > "$OUTPUT/$name.command.txt"
  printf '\n' >> "$OUTPUT/$name.command.txt"
  set +e
  "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
}

run_remote() {
  local name="$1"; shift
  printf 'adb -s %q shell %q\n' "$SERIAL" "$*" > "$OUTPUT/$name.command.txt"
  set +e
  "${ADB[@]}" shell "$*" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
}

run_local adb_state "${ADB[@]}" get-state
run_local adb_devices "${ADB[@]}" devices -l
run_remote identity 'id; getenforce; uname -a; getprop ro.build.fingerprint; getprop ro.build.version.incremental; getprop ro.build.version.security_patch'
run_remote all_getprop 'getprop'
run_remote ota_props 'getprop | grep -iE "ota|update|build|version|fingerprint|trona|ps7330"'
run_remote readable_ota_paths 'for d in /cache /data/ota /data/ota_package /data/local/tmp; do echo "[$d]"; ls -la "$d" 2>&1 | head -80; done'
run_remote ota_package_paths 'pm list packages -f | grep -iE "ota|update|provision|amazon.device.software"'
run_remote home_result 'cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME'

printf '# Phase 5T OTA metadata capture\n\n- Test ID: %s\n- Serial: %s\n- Timestamp UTC: %s\n- Read-only: yes\n- OTA/update operation: no\n- Device state mutation: no\n' \
  "$TEST_ID" "$SERIAL" "$STAMP" > "$OUTPUT/result.md"
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote read-only OTA metadata capture to %s\n' "$OUTPUT"
