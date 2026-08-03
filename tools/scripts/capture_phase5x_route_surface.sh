#!/usr/bin/env bash
# Capture a bounded, read-only Android route-surface snapshot.
# This script never opens a device node, reads a block device, writes to the
# device, starts an exploit, or changes package/settings state.
set -u
export LC_ALL=C

SERIAL=""
OUTPUT=""
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

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
      [ "$#" -ge 2 ] || die '--output requires a value'
      OUTPUT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      printf '%s\n' 'Usage: capture_phase5x_route_surface.sh --serial SERIAL --test-id TEST-ID --output DIR [--dry-run]'
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

[ -n "${SERIAL:-}" ] || die '--serial is required'
[ -n "${TEST_ID:-}" ] || die '--test-id is required'
[ -n "${OUTPUT:-}" ] || die '--output is required'
case "$OUTPUT" in
  /|.|..|""|/tmp|/var/tmp)
    die "unsafe output directory: $OUTPUT"
    ;;
esac

COMMAND_NAMES=(
  device_state
  identity
  props
  processes
  packages
  services
  init_paths
  node_metadata
  apex_property
  apex_paths
  apex_help
  home
)

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

printf 'test_id\t%s\nserial\t%s\nstart_utc\t%s\nmode\tread-only\n' \
  "$TEST_ID" "$SERIAL" "$START_UTC" > "$OUTPUT/metadata.tsv"

run_capture() {
  local name="$1"
  shift
  local stdout_file="$OUTPUT/${name}.stdout.txt"
  local stderr_file="$OUTPUT/${name}.stderr.txt"
  local command_file="$OUTPUT/${name}.command.txt"
  local exit_file="$OUTPUT/${name}.exit_code.txt"
  local rc

  printf '%q ' "$@" > "$command_file"
  printf '\n' >> "$command_file"
  "$@" > "$stdout_file" 2> "$stderr_file"
  rc=$?
  printf '%s\n' "$rc" > "$exit_file"
  printf '%s\t%s\t%s\n' "$name" "$rc" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$OUTPUT/metadata.tsv"
  return 0
}

# Identity and state. All commands below are read-only.
run_capture device_state "${ADB[@]}" get-state
run_capture identity "${ADB[@]}" shell id
run_capture props "${ADB[@]}" shell getprop
run_capture processes "${ADB[@]}" shell ps -A -o USER,PID,PPID,NAME,ARGS
run_capture packages "${ADB[@]}" shell pm list packages
run_capture services "${ADB[@]}" shell service list
run_capture init_paths "${ADB[@]}" shell find /vendor/etc/init /system/etc/init -maxdepth 1 -type f
run_capture node_metadata "${ADB[@]}" shell ls -lZ /dev/sspm /dev/block/by-name/spmfw /sys/class/misc/sspm
run_capture apex_property "${ADB[@]}" shell getprop ro.apex.updatable
run_capture apex_paths "${ADB[@]}" shell ls -ld /system/apex /vendor/apex /product/apex
run_capture apex_help "${ADB[@]}" shell cmd apexservice --help
run_capture home "${ADB[@]}" shell cmd package resolve-activity --brief \
  -a android.intent.action.MAIN -c android.intent.category.HOME

END_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'end_utc\t%s\n' "$END_UTC" >> "$OUTPUT/metadata.tsv"

cat > "$OUTPUT/commands.txt" <<EOF
All commands in this directory are read-only.
Device serial: $SERIAL
Test ID: $TEST_ID
Each command has matching .stdout.txt, .stderr.txt, and .exit_code.txt files.
No /dev node was opened by this script. No block device was read. No package, setting, overlay, or process state was changed.
EOF

cat > "$OUTPUT/result.md" <<EOF
# $TEST_ID

- Mode: read-only runtime visibility capture
- Serial: $SERIAL
- Start UTC: $START_UTC
- End UTC: $END_UTC
- Device writes: none
- Device nodes opened: none
- Block devices read: none
- Exploit or root code executed: none

Raw stdout, stderr, exit codes, and command lines are preserved beside this file.
EOF

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z |
  while IFS= read -r -d '' file; do
    shasum -a 256 "$file"
  done > "$OUTPUT/sha256sums.txt"

printf 'Captured read-only route surface in %s\n' "$OUTPUT"
