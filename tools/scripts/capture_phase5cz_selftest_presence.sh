#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: capture_phase5cz_selftest_presence.sh --serial SERIAL --output DIR [--dry-run]"
  echo "Read-only search for shipped futex/kselftest binaries; refuses overwrite."
}

SERIAL=""
OUTPUT=""
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --serial) SERIAL="${2:-}"; shift 2 ;;
    --output) OUTPUT="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$SERIAL" || -z "$OUTPUT" ]]; then usage >&2; exit 2; fi
if [[ "$DRY_RUN" -eq 1 ]]; then
  printf '%s\n' \
    "DRY-RUN: no device or filesystem changes" \
    "adb -s $SERIAL shell find <read-only system/vendor paths> -iname '*futex*'" \
    "adb -s $SERIAL shell find <read-only system/vendor paths> -iname '*kselftest*'" \
    "adb -s $SERIAL shell find <read-only system/vendor paths> -iname '*requeue*'"
  exit 0
fi
if [[ -e "$OUTPUT" ]]; then
  echo "Refusing to overwrite existing output: $OUTPUT" >&2
  exit 2
fi
command -v adb >/dev/null || { echo "adb not found" >&2; exit 2; }
mkdir -p "$OUTPUT"
adb_cmd() { adb -s "$SERIAL" "$@"; }
if ! adb_cmd get-state 2>/dev/null | grep -qx device; then
  echo "Serial is not connected in device state: $SERIAL" >&2
  exit 3
fi

date -u +%Y-%m-%dT%H:%M:%SZ > "$OUTPUT/timestamp_utc.txt"
cat > "$OUTPUT/commands.txt" <<EOF
scope=read-only
adb -s $SERIAL shell find /data/local/tmp /system/bin /system/xbin /system/lib64 /vendor/bin /vendor/lib64 /product/bin /product/lib64 /system_ext/bin /system_ext/lib64 -maxdepth 2 -type f -iname '*futex*'
adb -s $SERIAL shell find <same paths> -maxdepth 2 -type f -iname '*kselftest*'
adb -s $SERIAL shell find <same paths> -maxdepth 2 -type f -iname '*rtmutex*' -o -iname '*requeue*'
EOF
adb_cmd devices -l > "$OUTPUT/adb-devices.txt"
adb_cmd shell getprop ro.build.fingerprint > "$OUTPUT/build-fingerprint.txt"
adb_cmd shell 'for d in /data/local/tmp /system/bin /system/xbin /system/lib64 /vendor/bin /vendor/lib64 /product/bin /product/lib64 /system_ext/bin /system_ext/lib64; do echo ===$d; find "$d" -maxdepth 2 -type f \( -iname "*futex*" -o -iname "*kselftest*" -o -iname "*rtmutex*" -o -iname "*requeue*" \) 2>/dev/null | head -80; done' > "$OUTPUT/device-selftest-search.txt" 2>&1
{
  echo "source_index=artifacts/phase5/ps7331-local-nested-build-index-20260804-01/rtmutex-futex-paths.txt"
  rg -n 'tools/testing/selftests/futex|futex_requeue_pi' artifacts/phase5/ps7331-local-nested-build-index-20260804-01/rtmutex-futex-paths.txt || true
  echo "source_makefile=artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/Makefile:1141-1143,1354"
  sed -n '1139,1146p;1351,1358p' artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/Makefile
} > "$OUTPUT/source-selftest-index.txt"

matches="$(grep -E -c 'futex|kselftest|rtmutex|requeue' "$OUTPUT/device-selftest-search.txt" || true)"
{
  echo "device_matching_lines=$matches"
  echo "source_selftest_paths_present=true"
  echo "device_selftest_binary_observed=$([[ "$matches" -gt 0 ]] && echo true || echo false)"
  echo "scope=read-only; no selftest was copied, executed or invoked"
} > "$OUTPUT/result.md"
(cd "$OUTPUT" && shasum -a 256 * > sha256sums.txt)
echo "Wrote read-only selftest presence capture to $OUTPUT"
