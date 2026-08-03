#!/usr/bin/env bash
# Read-only pull of Bluetooth framework/HAL artifacts for offline analysis.
# Failed pulls are preserved as evidence; no privilege boundary is bypassed.
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
      printf '%s\n' 'Usage: pull_phase5j_bluetooth_artifacts.sh --serial SERIAL --output DIR [--dry-run]'
      exit 0
      ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac

REMOTE_PATHS=(
  /system/app/Bluetooth/Bluetooth.apk
  /system/app/Bluetooth/oat/arm64/Bluetooth.odex
  /system/app/Bluetooth/oat/arm64/Bluetooth.vdex
  /system/lib64/libbluetooth.so
  /system/lib64/libbluetooth_jni.so
  /system/lib64/libbluetooth-binder.so
  /system/lib64/android.hardware.bluetooth@1.0.so
  /system/lib64/android.hardware.bluetooth.a2dp@1.0.so
  /vendor/bin/hw/android.hardware.bluetooth@1.0-service-mediatek
  /vendor/lib/modules/bt_drv.ko
  /vendor/lib/modules/wmt_drv.ko
  /vendor/etc/permissions/android.hardware.bluetooth.xml
  /vendor/etc/permissions/android.hardware.bluetooth_le.xml
  /vendor/etc/init/android.hardware.bluetooth@1.0-service-mediatek.rc
  /vendor/etc/init/init.bt_drv.rc
  /vendor/etc/init/init.wmt_drv.rc
  /vendor/etc/init/btmac.rc
)

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: pull only the listed Bluetooth APK/library/HAL/config paths; no device mutation\n'
  printf 'DRY-RUN: serial=%s output=%s\n' "$SERIAL" "$OUTPUT"
  printf '%s\n' "${REMOTE_PATHS[@]}"
  exit 0
fi

command -v adb >/dev/null 2>&1 || die 'adb is required'
command -v shasum >/dev/null 2>&1 || die 'shasum is required'
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"
mkdir -p "$OUTPUT/files"

printf 'serial=%s\nstart_utc=%s\nmode=read-only-pull\n' \
  "$SERIAL" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.txt"
printf '%s\n' "${REMOTE_PATHS[@]}" > "$OUTPUT/remote-paths.txt"

run_capture() {
  local name="$1"
  local rc
  shift
  set +e
  "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  rc="$?"
  set -e
  printf '%s\n' "$rc" > "$OUTPUT/$name.exit_code.txt"
}

run_capture device-state adb -s "$SERIAL" get-state
run_capture device-id adb -s "$SERIAL" shell id
run_capture device-fingerprint adb -s "$SERIAL" shell getprop ro.build.fingerprint
run_capture device-security-patch adb -s "$SERIAL" shell getprop ro.build.version.security_patch
run_capture bluetooth-path adb -s "$SERIAL" shell pm path com.android.bluetooth

for remote in "${REMOTE_PATHS[@]}"; do
  safe_name="${remote#/}"
  safe_name="${safe_name//\//__}"
  target="$OUTPUT/files/$safe_name"
  run_capture "pull.$safe_name" adb -s "$SERIAL" pull "$remote" "$target"
done

printf 'end_utc=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$OUTPUT/metadata.txt"
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
