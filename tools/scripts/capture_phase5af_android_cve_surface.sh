#!/usr/bin/env bash
# Capture a bounded, read-only Android prerequisite surface for CVE reviews.
# This script never opens a device node, reads a block device, writes to the
# device, starts a native payload, or changes package/settings/process state.
set -u
export LC_ALL=C

SERIAL=""
TEST_ID=""
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
      printf '%s\n' 'Usage: capture_phase5af_android_cve_surface.sh --serial SERIAL --test-id TEST-ID --output DIR [--dry-run]'
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in
  /|.|..|""|/tmp|/var/tmp)
    die "unsafe output directory: $OUTPUT"
    ;;
esac

COMMAND_NAMES=(
  device_state identity props kernel_security
  user_namespace_limits module_surface xfrm_stats node_metadata node_access
  processes packages services home
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

# Identity and kernel security posture.
run_capture device_state "${ADB[@]}" get-state
run_capture identity "${ADB[@]}" shell id
run_capture props "${ADB[@]}" shell getprop
run_capture kernel_security "${ADB[@]}" shell 'for p in /proc/sys/kernel/randomize_va_space /proc/sys/kernel/kptr_restrict /proc/sys/kernel/perf_event_paranoid; do printf "[%s]\\n" "$p"; cat "$p" 2>&1; done'
run_capture user_namespace_limits "${ADB[@]}" shell 'for p in /proc/sys/user/max_user_namespaces /proc/sys/kernel/unprivileged_userns_clone; do printf "[%s]\\n" "$p"; cat "$p" 2>&1; done'

# Read-only module and network-surface metadata. Missing paths are expected and
# are preserved with their exit codes/stderr.
run_capture module_surface "${ADB[@]}" shell 'for p in /sys/module/xt_TEE /sys/module/esp4 /sys/module/esp6 /sys/module/x_tables /sys/module/xfrm_user /sys/module/ipv6; do ls -ld "$p" 2>&1; done; printf "[proc_modules]\n"; grep -iE "(^| )(xt_TEE|esp4|esp6|x_tables|xfrm_user|ipv6)( |$)" /proc/modules 2>&1'
run_capture xfrm_stats "${ADB[@]}" shell cat /proc/net/xfrm_stat

# Metadata/access checks only: no open/read/ioctl is attempted on these nodes.
run_capture node_metadata "${ADB[@]}" shell ls -lZ /dev/ion /dev/aed0 /dev/aed1 /dev/atf_log /dev/sspm /dev/block/by-name/spmfw
run_capture node_access "${ADB[@]}" shell 'for node in /dev/ion /dev/aed0 /dev/aed1 /dev/atf_log /dev/sspm; do if test -r "$node"; then r=1; else r=0; fi; if test -w "$node"; then w=1; else w=0; fi; printf "%s read=%s write=%s\\n" "$node" "$r" "$w"; done'

# Bounded visibility checks for Android/vendor implementations.
run_capture processes "${ADB[@]}" shell ps -A -o USER,PID,NAME,ARGS
run_capture packages "${ADB[@]}" shell pm list packages
run_capture services "${ADB[@]}" shell service list
run_capture home "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME

END_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'end_utc\t%s\n' "$END_UTC" >> "$OUTPUT/metadata.tsv"

printf '%s\n' \
  'All commands in this directory are read-only.' \
  "Device serial: $SERIAL" \
  "Test ID: $TEST_ID" \
  'Each command has matching .stdout.txt, .stderr.txt, and .exit_code.txt files.' \
  'No device node was opened. No block device was read. No package, setting, overlay, process, or network state was changed.' \
  > "$OUTPUT/commands.txt"

printf '# %s\n\n- Mode: read-only Android CVE prerequisite capture\n- Serial: %s\n- Start UTC: %s\n- End UTC: %s\n- Device writes: none\n- Device nodes opened: none\n- Block devices read: none\n- Exploit or root code executed: none\n\nRaw stdout, stderr, exit codes, and command lines are preserved beside this file.\n' \
  "$TEST_ID" "$SERIAL" "$START_UTC" "$END_UTC" > "$OUTPUT/result.md"

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z |
  while IFS= read -r -d '' file; do
    shasum -a 256 "$file"
  done > "$OUTPUT/sha256sums.txt"

printf 'Captured read-only Android CVE surface in %s\n' "$OUTPUT"
