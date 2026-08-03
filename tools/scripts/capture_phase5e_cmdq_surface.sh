#!/usr/bin/env bash
set -Eeuo pipefail

SERIAL=""
OUTPUT=""
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: capture_phase5e_cmdq_surface.sh --serial SERIAL --output DIR [--dry-run]'
      exit 0
      ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac

ADB_BIN="${ADB_BIN:-adb}"
command -v "$ADB_BIN" >/dev/null 2>&1 || die "adb not found: $ADB_BIN"

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: adb -s %q get-state\n' "$SERIAL"
  printf 'DRY-RUN: adb -s %q shell getprop / getenforce / id / ls -lZ /dev/mtk_cmdq\n' "$SERIAL"
  printf '%s\n' 'DRY-RUN: no exploit, file push, package mutation, reboot, or partition operation'
  exit 0
fi

[ ! -e "$OUTPUT" ] || die "output directory already exists: $OUTPUT"
mkdir -p "$OUTPUT"
OUTPUT="$(cd "$OUTPUT" && pwd)"

timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'test_id=PHASE5E-CMDQ-SURFACE-%s\nserial=%s\ntimestamp_utc=%s\noperation=read_only_cmdq_surface_inventory\ndevice_mutation=none\n' \
  "$(date -u '+%Y%m%d-%H%M%S')" "$SERIAL" "$timestamp" > "$OUTPUT/metadata.tsv"

run_capture() {
  local name="$1"
  shift
  printf '%s\n' "$*" > "$OUTPUT/$name.command.txt"
  set +e
  "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local code=$?
  set -e
  printf '%s\n' "$code" > "$OUTPUT/$name.exit_code.txt"
}

run_capture adb_state "$ADB_BIN" -s "$SERIAL" get-state
run_capture model "$ADB_BIN" -s "$SERIAL" shell getprop ro.product.model
run_capture product "$ADB_BIN" -s "$SERIAL" shell getprop ro.product.device
run_capture fingerprint "$ADB_BIN" -s "$SERIAL" shell getprop ro.build.fingerprint
run_capture security_patch "$ADB_BIN" -s "$SERIAL" shell getprop ro.build.version.security_patch
run_capture kernel "$ADB_BIN" -s "$SERIAL" shell cat /proc/version
run_capture selinux "$ADB_BIN" -s "$SERIAL" shell getenforce
run_capture shell_id "$ADB_BIN" -s "$SERIAL" shell id
run_capture shell_context "$ADB_BIN" -s "$SERIAL" shell cat /proc/self/attr/current
run_capture cmdq_node "$ADB_BIN" -s "$SERIAL" shell ls -lZ /dev/mtk_cmdq
run_capture cmdq_access "$ADB_BIN" -s "$SERIAL" shell 'test -r /dev/mtk_cmdq; echo readable=$?; test -w /dev/mtk_cmdq; echo writable=$?'
run_capture cmdq_devices "$ADB_BIN" -s "$SERIAL" shell 'ls -l /dev 2>&1'
run_capture cmdq_misc "$ADB_BIN" -s "$SERIAL" shell 'ls -l /sys/class/misc 2>&1'
run_capture cmdq_modules "$ADB_BIN" -s "$SERIAL" shell 'cat /proc/modules 2>&1'

cat > "$OUTPUT/result.md" <<'EOF'
# Phase 5E CMDQ surface inventory

This directory contains read-only Android shell observations. It does not
execute `mtk-su`, issue CMDQ ioctls, push a binary, change SELinux, reboot, or
write a partition.

Interpret the presence of `/dev/mtk_cmdq` only as an exposed driver surface;
it is not proof that CVE-2020-0069 remains exploitable on this build.
EOF

if command -v shasum >/dev/null 2>&1; then
  (cd "$OUTPUT" && find . -type f ! -name sha256sums.txt -print | sort | sed 's#^./##' | xargs shasum -a 256) > "$OUTPUT/sha256sums.txt"
else
  (cd "$OUTPUT" && find . -type f ! -name sha256sums.txt -print | sort | sed 's#^./##' | xargs sha256sum) > "$OUTPUT/sha256sums.txt"
fi
printf 'Wrote read-only CMDQ surface evidence to %s\n' "$OUTPUT"
