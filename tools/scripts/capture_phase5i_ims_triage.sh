#!/usr/bin/env bash
# Read-only MT8183 IMS/ATCI applicability triage.
# This script never sets a property, starts/stops a service, sends an AT
# command, invokes a Binder transaction, changes package state, or reboots.
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
      printf '%s\n' 'Usage: capture_phase5i_ims_triage.sh --serial SERIAL --output DIR [--dry-run]'
      exit 0
      ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: collect getprop, service/package/process lists, dumpsys, vendor init rc, and telephony dumps\n'
  printf 'DRY-RUN: serial=%s output=%s; no mutation command is present\n' "$SERIAL" "$OUTPUT"
  exit 0
fi

command -v adb >/dev/null 2>&1 || die 'adb is required'
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"
mkdir -p "$OUTPUT"

printf 'test_id=%s\nserial=%s\nstart_utc=%s\nmode=read-only\n' \
  "$(basename "$OUTPUT")" "$SERIAL" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.txt"

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

cat > "$OUTPUT/commands.txt" <<EOF
adb -s $SERIAL get-state
adb -s $SERIAL shell id
adb -s $SERIAL shell getprop
adb -s $SERIAL shell getenforce
adb -s $SERIAL shell service list
adb -s $SERIAL shell dumpsys -l
adb -s $SERIAL shell pm list packages -f
adb -s $SERIAL shell pm list permissions -g
adb -s $SERIAL shell ps -A -o USER,PID,PPID,NAME,ARGS
adb -s $SERIAL shell ls -la /vendor/bin
adb -s $SERIAL shell ls -la /vendor/bin/hw
adb -s $SERIAL shell ls -la /vendor/lib64
adb -s $SERIAL shell find /vendor/etc -type f
adb -s $SERIAL shell find /system/etc -type f
adb -s $SERIAL shell dumpsys package
adb -s $SERIAL shell dumpsys activity services
adb -s $SERIAL shell dumpsys device_policy
adb -s $SERIAL shell dumpsys telephony.registry
adb -s $SERIAL shell dumpsys phone
adb -s $SERIAL shell dumpsys isms
adb -s $SERIAL shell cat /vendor/etc/init/atcid.rc
adb -s $SERIAL shell cat /vendor/etc/init/audiocmdservice_atci.rc
adb -s $SERIAL shell cat /vendor/etc/init/hw/init.modem.rc
adb -s $SERIAL shell cat /vendor/etc/init/hw/meta_init.modem.rc
adb -s $SERIAL shell getprop persist.vendor.service.atci.autostart
adb -s $SERIAL shell getprop persist.vendor.service.atci.atm_mode
adb -s $SERIAL shell getprop vendor.mtk.atci.boot_completed
adb -s $SERIAL shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
EOF

run_capture device.get-state adb -s "$SERIAL" get-state
run_capture device.id adb -s "$SERIAL" shell id
run_capture device.getprop adb -s "$SERIAL" shell getprop
run_capture device.getenforce adb -s "$SERIAL" shell getenforce
run_capture device.service-list adb -s "$SERIAL" shell service list
run_capture device.dumpsys-list adb -s "$SERIAL" shell dumpsys -l
run_capture device.packages adb -s "$SERIAL" shell pm list packages -f
run_capture device.permissions adb -s "$SERIAL" shell pm list permissions -g
run_capture device.ps adb -s "$SERIAL" shell ps -A -o USER,PID,PPID,NAME,ARGS
run_capture device.vendor-bin adb -s "$SERIAL" shell ls -la /vendor/bin
run_capture device.vendor-bin-hw adb -s "$SERIAL" shell ls -la /vendor/bin/hw
run_capture device.vendor-lib64 adb -s "$SERIAL" shell ls -la /vendor/lib64
run_capture device.vendor-etc-files adb -s "$SERIAL" shell find /vendor/etc -type f
run_capture device.system-etc-files adb -s "$SERIAL" shell find /system/etc -type f
run_capture device.dumpsys-package adb -s "$SERIAL" shell dumpsys package
run_capture device.dumpsys-activity-services adb -s "$SERIAL" shell dumpsys activity services
run_capture device.dumpsys-device-policy adb -s "$SERIAL" shell dumpsys device_policy
run_capture device.dumpsys-telephony-registry adb -s "$SERIAL" shell dumpsys telephony.registry
run_capture device.dumpsys-phone adb -s "$SERIAL" shell dumpsys phone
run_capture device.dumpsys-isms adb -s "$SERIAL" shell dumpsys isms
run_capture atcid-rc adb -s "$SERIAL" shell cat /vendor/etc/init/atcid.rc
run_capture audiocmdservice-atci-rc adb -s "$SERIAL" shell cat /vendor/etc/init/audiocmdservice_atci.rc
run_capture init-modem-rc adb -s "$SERIAL" shell cat /vendor/etc/init/hw/init.modem.rc
run_capture meta-init-modem-rc adb -s "$SERIAL" shell cat /vendor/etc/init/hw/meta_init.modem.rc
run_capture atci-autostart adb -s "$SERIAL" shell getprop persist.vendor.service.atci.autostart
run_capture atci-atm-mode adb -s "$SERIAL" shell getprop persist.vendor.service.atci.atm_mode
run_capture atci-boot-completed adb -s "$SERIAL" shell getprop vendor.mtk.atci.boot_completed
run_capture device.home adb -s "$SERIAL" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME

rg -i 'com\\.(mediatek|android)\\.(ims|imss|imsservice)|imsservice|ImsService|atci|atcmd|libims' \
  "$OUTPUT/device.packages.stdout.txt" "$OUTPUT/device.dumpsys-package.stdout.txt" \
  "$OUTPUT/device.ps.stdout.txt" "$OUTPUT/device.service-list.stdout.txt" > "$OUTPUT/filtered-ims-atci.txt" || true
rg -i 'atci|atcmd|ril|radio|modem|ims|telephony' "$OUTPUT/device.vendor-etc-files.stdout.txt" > "$OUTPUT/filtered-vendor-etc.txt" || true
rg -i -n -C 3 'ims|telephony|radio|ril|modem|atci|atcmd|baseband|sim' \
  "$OUTPUT/device.dumpsys-telephony-registry.stdout.txt" "$OUTPUT/device.dumpsys-phone.stdout.txt" \
  "$OUTPUT/device.dumpsys-isms.stdout.txt" > "$OUTPUT/filtered-telephony-dumps.txt" || true

printf 'end_utc=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$OUTPUT/metadata.txt"
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
