#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: capture_phase5db_exact_ps7331_match.sh --serial SERIAL --ota-prop FILE --output DIR [--dry-run]"
}

SERIAL=""
OTA_PROP=""
OUTPUT=""
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --serial) SERIAL="${2:-}"; shift 2 ;;
    --ota-prop) OTA_PROP="${2:-}"; shift 2 ;;
    --output) OUTPUT="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$SERIAL" || -z "$OTA_PROP" || -z "$OUTPUT" ]]; then
  usage >&2
  exit 2
fi
if [[ "$DRY_RUN" -eq 1 ]]; then
  printf '%s\n' \
    "DRY-RUN: no device or filesystem changes" \
    "adb -s $SERIAL shell getprop ro.build.fingerprint" \
    "adb -s $SERIAL shell getprop ro.build.version.incremental" \
    "adb -s $SERIAL shell getprop ro.build.version.security_patch" \
    "compare with $OTA_PROP"
  exit 0
fi
if [[ -e "$OUTPUT" ]]; then
  echo "Refusing to overwrite existing output: $OUTPUT" >&2
  exit 2
fi
if [[ ! -f "$OTA_PROP" ]]; then
  echo "OTA property file not found: $OTA_PROP" >&2
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
printf '%s\n' \
  "scope=read-only" \
  "adb -s $SERIAL shell getprop" \
  "adb -s $SERIAL shell id" \
  "adb -s $SERIAL shell uname -a" \
  "adb -s $SERIAL shell getprop ro.boot.verifiedbootstate" \
  "adb -s $SERIAL shell getprop ro.boot.flash.locked" \
  "host compare with $OTA_PROP" > "$OUTPUT/commands.txt"

adb_cmd devices -l > "$OUTPUT/adb-devices.txt"
adb_cmd shell getprop > "$OUTPUT/device-getprop.txt"
adb_cmd shell id > "$OUTPUT/device-id.txt"
adb_cmd shell uname -a > "$OUTPUT/device-uname.txt"
adb_cmd shell getprop ro.boot.verifiedbootstate > "$OUTPUT/verifiedbootstate.txt"
adb_cmd shell getprop ro.boot.flash.locked > "$OUTPUT/flash-locked.txt"

getprop_file() {
  local key="$1"
  adb_cmd shell getprop "$key" | tr -d '\r'
}

DEVICE_FINGERPRINT="$(getprop_file ro.build.fingerprint)"
DEVICE_INCREMENTAL="$(getprop_file ro.build.version.incremental)"
DEVICE_PATCH="$(getprop_file ro.build.version.security_patch)"
DEVICE_PRODUCT="$(getprop_file ro.product.device)"
DEVICE_MODEL="$(getprop_file ro.product.model)"

ota_prop() {
  local key="$1"
  awk -F= -v wanted="$key" '$1 == wanted { sub(/^[^=]*=/, ""); print; exit }' "$OTA_PROP"
}

OTA_DESCRIPTION="$(ota_prop description)"
OTA_INCREMENTAL="$(ota_prop version_number)"
OTA_PRODUCT="$(ota_prop product)"
OTA_PATCH="$(sed -n 's/^post-security-patch-level=//p' "${OTA_PROP%/*}/android-metadata.txt" 2>/dev/null | head -1 || true)"

fingerprint_match=false
incremental_match=false
product_match=false
patch_match=false
[[ "$DEVICE_FINGERPRINT" == "$OTA_DESCRIPTION" ]] && fingerprint_match=true
[[ "$DEVICE_INCREMENTAL" == "$OTA_INCREMENTAL" ]] && incremental_match=true
[[ "$DEVICE_PRODUCT" == "$OTA_PRODUCT" ]] && product_match=true
if [[ -n "$OTA_PATCH" && "$DEVICE_PATCH" == "$OTA_PATCH" ]]; then patch_match=true; fi

printf '%s\n' "$DEVICE_FINGERPRINT" > "$OUTPUT/device-fingerprint.txt"
printf '%s\n' "$DEVICE_INCREMENTAL" > "$OUTPUT/device-incremental.txt"
printf '%s\n' "$DEVICE_PATCH" > "$OUTPUT/device-security-patch.txt"
printf '%s\n' "$DEVICE_PRODUCT" > "$OUTPUT/device-product.txt"
printf '%s\n' "$DEVICE_MODEL" > "$OUTPUT/device-model.txt"
printf '%s\n' "$OTA_DESCRIPTION" > "$OUTPUT/ota-description.txt"
printf '%s\n' "$OTA_INCREMENTAL" > "$OUTPUT/ota-version-number.txt"
printf '%s\n' "$OTA_PRODUCT" > "$OUTPUT/ota-product.txt"
printf '%s\n' "$OTA_PATCH" > "$OUTPUT/ota-security-patch.txt"

all_match=false
if [[ "$fingerprint_match" == true && "$incremental_match" == true && "$product_match" == true && "$patch_match" == true ]]; then
  all_match=true
fi

printf '%s\n' \
  "fingerprint_match=$fingerprint_match" \
  "incremental_match=$incremental_match" \
  "product_match=$product_match" \
  "security_patch_match=$patch_match" \
  "exact_target_match=$all_match" \
  "scope=read-only; no mutation, reboot, futex, exploit, or root operation" > "$OUTPUT/result.md"

printf '{\n  "device_fingerprint": "%s",\n  "device_incremental": "%s",\n  "device_security_patch": "%s",\n  "device_product": "%s",\n  "device_model": "%s",\n  "ota_description": "%s",\n  "ota_version_number": "%s",\n  "ota_product": "%s",\n  "ota_security_patch": "%s",\n  "fingerprint_match": %s,\n  "incremental_match": %s,\n  "product_match": %s,\n  "security_patch_match": %s,\n  "exact_target_match": %s,\n  "device_io_scope": "read-only"\n}\n' \
  "$DEVICE_FINGERPRINT" "$DEVICE_INCREMENTAL" "$DEVICE_PATCH" "$DEVICE_PRODUCT" "$DEVICE_MODEL" \
  "$OTA_DESCRIPTION" "$OTA_INCREMENTAL" "$OTA_PRODUCT" "$OTA_PATCH" \
  "$fingerprint_match" "$incremental_match" "$product_match" "$patch_match" "$all_match" > "$OUTPUT/metadata.json"

(cd "$OUTPUT" && find . -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > sha256sums.txt)
echo "Wrote exact PS7331 match capture to $OUTPUT"
