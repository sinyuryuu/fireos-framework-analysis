#!/usr/bin/env bash
# Read-only runtime gate capture for static GhostLock applicability review.
# Never triggers futex PI, opens a device node, changes a sysctl, reboots, or
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
      printf '%s\n' 'Usage: capture_phase5p_futex_gates.sh --serial SERIAL --test-id ID --output DIR [--dry-run]'
      exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$OUTPUT" ] || die '--output is required'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: verify adb -s %q get-state\n' "$SERIAL"
  printf '%s\n' 'DRY-RUN: read kernel sysctls, /proc status, security properties, and node permissions only'
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
run_remote identity 'id; getenforce; uname -a; getprop ro.build.fingerprint; getprop ro.build.version.incremental'
run_remote cmdline 'cat /proc/cmdline'
run_remote kernel_sysctls 'for p in /proc/sys/kernel/panic_on_oops /proc/sys/kernel/panic /proc/sys/kernel/panic_on_warn /proc/sys/kernel/kptr_restrict /proc/sys/kernel/dmesg_restrict /proc/sys/kernel/perf_event_paranoid /proc/sys/kernel/randomize_va_space /proc/sys/kernel/yama/ptrace_scope /proc/sys/kernel/unprivileged_userns_clone /proc/sys/kernel/unprivileged_bpf_disabled; do echo "--- $p"; cat "$p" 2>&1; done'
run_remote process_status 'grep -E "^(Name|Uid|Gid|Groups|CapInh|CapPrm|CapEff|CapBnd|NoNewPrivs|Seccomp|Seccomp_filters):" /proc/self/status'
run_remote proc_visibility 'ls -lZ /proc/kallsyms /proc/kcore /dev/kmem /dev/ion /dev/mtk_cmdq 2>&1; echo "--- kallsyms ---"; head -20 /proc/kallsyms 2>&1'
run_remote futex_symbols 'grep -E "futex|rt_mutex|remove_waiter|proxy_lock" /proc/kallsyms 2>&1 | head -80'

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
cat > "$OUTPUT/result.md" <<EOF
# Phase 5P futex applicability gates

- Test ID: $TEST_ID
- Serial: $SERIAL
- Timestamp UTC: $STAMP
- Read-only: yes
- Futex/PI trigger: no
- Device state mutation: no

Failures of individual read-only proc/sysctl reads are preserved and are not
treated as evidence that a feature is enabled or disabled.
EOF
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote read-only futex gate capture to %s\n' "$OUTPUT"
