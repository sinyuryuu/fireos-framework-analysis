#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 --serial SERIAL --output DIR" >&2
  exit 2
}

serial=""
output=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --serial) [[ $# -ge 2 ]] || usage; serial="$2"; shift 2 ;;
    --output) [[ $# -ge 2 ]] || usage; output="$2"; shift 2 ;;
    *) usage ;;
  esac
done
[[ -n "$serial" && -n "$output" ]] || usage
command -v adb >/dev/null || { echo "adb not found" >&2; exit 1; }
[[ ! -e "$output" ]] || { echo "refusing to overwrite existing output: $output" >&2; exit 1; }
mkdir -p "$output"

adb devices -l >"$output/adb_devices.txt"
adb -s "$serial" get-serialno >"$output/serial.txt"
adb -s "$serial" shell getprop ro.build.fingerprint >"$output/build_fingerprint.txt"
adb -s "$serial" shell getprop ro.build.version.incremental >"$output/build_incremental.txt"
adb -s "$serial" shell 'ls -l /system/etc/*policy* /system/etc/*Policy* /vendor/etc/*policy* /product/etc/*policy* /system_ext/etc/*policy* 2>&1' >"$output/device_policy_paths.txt"

for name in global_policy.xml common_device_policy.xml product_policy.xml multimodal_device_policy.xml receiver_filter_policy.xml; do
  adb -s "$serial" pull "/system/etc/$name" "$output/$name" >"$output/pull_${name}.log" 2>&1 || true
done

date -u '+%Y-%m-%dT%H:%M:%SZ' >"$output/captured_at_utc.txt"
sha256sum "$output"/* >"$output/sha256sums.txt"
