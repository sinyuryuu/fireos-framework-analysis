#!/usr/bin/env bash
# Read-only post-check for Phase 5BA. No reboot, setting, package, or image operation.
set -Eeuo pipefail
export LC_ALL=C

SERIAL=""
OUTPUT=""
DRY_RUN=0
die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }
while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) printf '%s\n' 'Usage: capture_phase5ba_device_postcheck.sh --serial SERIAL --output DIR [--dry-run]'; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done
[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in /|.|..|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac
if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: adb -s %s read-only identity, build, HOME resolver and Fire Launcher path into %s\n' "$SERIAL" "$OUTPUT"
  exit 0
fi
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"
command -v adb >/dev/null 2>&1 || die 'adb not found'
mkdir -p "$OUTPUT"
OUTPUT="$(cd "$OUTPUT" && pwd)"
STAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'serial=%s\ntimestamp_utc=%s\nmode=read_only\n' "$SERIAL" "$STAMP" > "$OUTPUT/metadata.tsv"
run() {
  local name="$1"; shift
  printf 'adb -s %q %q' "$SERIAL" "$1" > "$OUTPUT/$name.command.txt"
  for arg in "${@:2}"; do printf ' %q' "$arg" >> "$OUTPUT/$name.command.txt"; done
  printf '\n' >> "$OUTPUT/$name.command.txt"
  set +e
  adb -s "$SERIAL" "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local code=$?
  set -e
  printf '%s\n' "$code" > "$OUTPUT/$name.exit_code.txt"
}
run get_state get-state
run fingerprint shell getprop ro.build.fingerprint
run incremental shell getprop ro.build.version.incremental
run security_patch shell getprop ro.build.version.security_patch
run resolver shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
run firelauncher_path shell pm path com.amazon.firelauncher
run firelauncher_dump shell dumpsys package com.amazon.firelauncher
run activity_top shell dumpsys activity activities
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote read-only post-check to %s\n' "$OUTPUT"
