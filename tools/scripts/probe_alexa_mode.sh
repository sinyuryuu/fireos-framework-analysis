#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
OUTPUT=''
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: probe_alexa_mode.sh --serial SERIAL --output DIR [--dry-run]

Collects read-only observations for Amazon's alexa_modeswitch service and the
mss_mode secure setting. It does not change settings, switch modes, reboot,
launch an activity, or alter package state.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial)
      [ "$#" -ge 2 ] || die '--serial requires a value'
      SERIAL="$2"
      shift 2
      ;;
    --output)
      [ "$#" -ge 2 ] || die '--output requires a path'
      OUTPUT="$2"
      shift 2
      ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$OUTPUT" ] || die '--output is required'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: serial=%s output=%s\n' "$SERIAL" "$OUTPUT"
  printf "DRY-RUN: adb -s '%s' get-state\n" "$SERIAL"
  printf "DRY-RUN: adb -s '%s' shell service list\n" "$SERIAL"
  printf "DRY-RUN: adb -s '%s' shell dumpsys alexa_modeswitch\n" "$SERIAL"
  printf "DRY-RUN: adb -s '%s' shell settings get secure mss_mode\n" "$SERIAL"
  printf "DRY-RUN: adb -s '%s' shell service call alexa_modeswitch 2\n" "$SERIAL"
  printf 'DRY-RUN: raw outputs, command manifest, summary and SHA-256 manifest would be written under %s\n' "$OUTPUT"
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

run_adb_capture 'get_state' yes "$OUTPUT/get_state.txt" get-state
run_adb_capture 'service_list' yes "$OUTPUT/service_list.txt" shell service list
run_adb_capture 'dumpsys_alexa_modeswitch' no "$OUTPUT/dumpsys_alexa_modeswitch.txt" shell dumpsys alexa_modeswitch
run_adb_capture 'secure_mss_mode' no "$OUTPUT/secure_mss_mode.txt" shell settings get secure mss_mode
run_adb_capture 'service_call_get_mode' no "$OUTPUT/service_call_get_mode.txt" shell service call alexa_modeswitch 2

{
  printf '# Alexa mode read-only probe\n\n'
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- Collected at (UTC): `%s`\n' "$(timestamp_utc)"
  printf -- '- Hard command failures: `%s`\n' "$HARD_FAILURES"
  printf -- '- Finding status: `Hypothesis` until the raw outputs and framework code are reviewed.\n\n'
  printf '## Commands and outputs\n\n'
  printf -- '- [Command manifest](command_manifest.tsv)\n'
  printf -- '- [Service list](service_list.txt)\n'
  printf -- '- [dumpsys alexa_modeswitch](dumpsys_alexa_modeswitch.txt)\n'
  printf -- '- [secure mss_mode](secure_mss_mode.txt)\n'
  printf -- '- [Binder transaction 2 getMode probe](service_call_get_mode.txt)\n'
  printf -- '- [SHA-256 manifest](sha256sums.txt)\n\n'
  printf 'This probe is observational only. Transaction 2 is identified as getMode() in the extracted IAlexaModeSwitchService proxy; a shell error is retained as evidence of service observability, not treated as a mode value.\n'
} > "$OUTPUT/test_summary.md"

write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"

if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'Alexa mode probe completed with %s required command failure(s): %s\n' "$HARD_FAILURES" "$OUTPUT" >&2
  exit 2
fi
printf 'Alexa mode probe completed: %s\n' "$OUTPUT"
