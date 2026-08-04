#!/usr/bin/env bash
# Read-only PS7331 kernel-config and tracing-visibility capture.
set -Eeuo pipefail
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
    -h|--help)
      printf '%s\n' 'Usage: capture_phase5cm_config_gates.sh --serial SERIAL --test-id ID --output DIR [--dry-run]'
      exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$OUTPUT" ] || die '--output is required'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: adb -s %q read-only kernel config and debugfs visibility capture\n' "$SERIAL"
  printf 'DRY-RUN: write raw outputs and SHA-256 manifest under %q\n' "$OUTPUT"
  exit 0
fi

case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"
command -v adb >/dev/null 2>&1 || die 'adb not found'
mkdir -p "$OUTPUT"

STAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'test_id=%s\nserial=%s\ntimestamp_utc=%s\nread_only=true\n' \
  "$TEST_ID" "$SERIAL" "$STAMP" > "$OUTPUT/metadata.tsv"

run() {
  local name="$1"; shift
  printf 'adb -s %q' "$SERIAL" > "$OUTPUT/$name.command.txt"
  printf ' %q' "$@" >> "$OUTPUT/$name.command.txt"
  printf '\n' >> "$OUTPUT/$name.command.txt"
  set +e
  adb -s "$SERIAL" "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
}

run adb_state get-state
run identity shell 'id; getenforce; uname -a; getprop ro.build.fingerprint; getprop ro.build.version.incremental'
run config shell 'if [ -r /proc/config.gz ]; then zcat /proc/config.gz 2>&1 | grep -E "CONFIG_(FUTEX|RT_MUTEX|HAVE_FUTEX|SECCOMP|SECURITY_SELINUX|DEBUG_FS|KALLSYMS)"; else echo CONFIG_NOT_READABLE_OR_ABSENT; fi'
run tracing_paths shell 'ls -ldZ /sys/kernel/debug /sys/kernel/debug/tracing /sys/kernel/debug/tracing/events 2>&1'
run tracing_listing shell 'ls -laZ /sys/kernel/debug /sys/kernel/debug/tracing /sys/kernel/debug/tracing/events 2>&1'
run tracing_event_categories shell 'ls -1 /sys/kernel/debug/tracing/events 2>&1'
run futex_event_search shell 'printf "%s\\n" "-- categories --"; ls -1 /sys/kernel/debug/tracing/events 2>&1 | grep -Ei "futex|rtmutex" || true; printf "%s\\n" "-- scheduler/task categories --"; ls -1 /sys/kernel/debug/tracing/events 2>&1 | grep -Ei "sched|task|lock" || true'
run mounts shell 'mount | grep -E "(/proc |debugfs|tracefs)" 2>&1'

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
cat > "$OUTPUT/result.md" <<EOF
# Phase 5CM PS7331 kernel-config and tracing visibility capture

- Test ID: $TEST_ID
- Timestamp UTC: $STAMP
- Read-only: yes
- Futex/PI trigger: no
- Device-node open/ioctl: no
- Device state mutation: no

Permission failures are preserved and are not interpreted as feature absence.
EOF
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote read-only config gate capture to %s\n' "$OUTPUT"
