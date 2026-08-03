#!/usr/bin/env bash
set -Eeuo pipefail

SERIAL=""
TEST_ID=""
OUTPUT=""
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  capture_phase5al_mtk_cve_surface.sh \
    --serial SERIAL --test-id TEST_ID --output OUTPUT [--dry-run]

Read-only exact-device surface triage for MediaTek Android CVE candidates.
It does not open device nodes, call ioctl, send modem/AT traffic, trigger a
race, write Settings, change package state, reboot, or touch boot partitions.
EOF
}

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
      usage
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
[ "$OUTPUT" != "/" ] && [ "$OUTPUT" != "." ] && [ "$OUTPUT" != ".." ] || die 'unsafe output path'

ADB=(adb -s "$SERIAL")

if [ "$DRY_RUN" -eq 1 ]; then
  cat <<EOF
DRY-RUN: ${ADB[*]} get-state
DRY-RUN: ${ADB[*]} shell getprop
DRY-RUN: ${ADB[*]} shell service list
DRY-RUN: ${ADB[*]} shell ps -A
DRY-RUN: ${ADB[*]} shell pm list packages
DRY-RUN: ${ADB[*]} shell dumpsys telephony.registry
DRY-RUN: ${ADB[*]} shell dumpsys phone
DRY-RUN: ${ADB[*]} shell ls -l <candidate device nodes>
DRY-RUN: ${ADB[*]} shell cat /proc/modules
DRY-RUN: ${ADB[*]} shell cat <read-only kernel sysctls>
EOF
  exit 0
fi

[ ! -e "$OUTPUT" ] || die "refusing to overwrite existing output: $OUTPUT"
mkdir -p "$OUTPUT"

run_capture() {
  local name="$1"
  shift
  printf '%s\n' "${ADB[*]} $*" > "$OUTPUT/$name.command.txt"
  set +e
  "${ADB[@]}" "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
}

run_capture devices get-state
run_capture id shell id
run_capture fingerprint shell getprop ro.build.fingerprint
run_capture model shell getprop ro.product.model
run_capture device shell getprop ro.product.device
run_capture hardware shell getprop ro.hardware
run_capture os shell getprop ro.build.version.release
run_capture sdk shell getprop ro.build.version.sdk
run_capture patch shell getprop ro.build.version.security_patch
run_capture kernel shell uname -a
run_capture enforce shell getenforce
run_capture packages shell pm list packages
run_capture packages_filtered shell 'pm list packages | grep -iE "ims|radio|telephony|phone|mtk|modem|mobile|connsys|vpu|mdp|ged|ssmr|ccci|atf|spm" || true'
run_capture services shell service list
run_capture services_filtered shell 'service list | grep -iE "ims|radio|telephony|phone|mtk|modem|mobile|connsys|vpu|mdp|ged|ssmr|ccci|atf|spm" || true'
run_capture processes shell ps -A
run_capture processes_filtered shell 'ps -A | grep -iE "ims|radio|telephony|phone|mtk|modem|mobile|connsys|vpu|mdp|ged|ssmr|ccci|atf|spm" | grep -v grep || true'
run_capture telephony_registry shell dumpsys telephony.registry
run_capture phone_dump shell dumpsys phone
run_capture radio_dump shell dumpsys radio
run_capture device_nodes shell 'for p in /dev/ion /dev/aed0 /dev/aed1 /dev/atf_log /dev/sspm /dev/ccci* /dev/ccci_md* /dev/mdp* /dev/vpu* /dev/ged* /dev/mtk* /dev/mst* /dev/ttyC*; do ls -ld "$p" 2>&1 || true; done'
run_capture proc_modules shell cat /proc/modules
run_capture proc_devices shell cat /proc/devices
run_capture kernel_surfaces shell 'for p in /proc/sys/kernel/perf_event_paranoid /proc/sys/kernel/kptr_restrict /proc/sys/kernel/dmesg_restrict /proc/sys/kernel/unprivileged_bpf_disabled /proc/sys/user/max_user_namespaces /proc/sys/kernel/unprivileged_userns_clone; do if [ -r "$p" ]; then printf "%s=" "$p"; cat "$p"; else printf "%s=NOT_PRESENT_OR_UNREADABLE\n" "$p"; fi; done'
run_capture binary_names shell 'for d in /system/bin /system/xbin /vendor/bin /vendor/bin/hw /system/vendor/bin; do if [ -d "$d" ]; then find "$d" -maxdepth 1 -type f \( -iname "*ims*" -o -iname "*mobile*" -o -iname "*radio*" -o -iname "*modem*" -o -iname "*ccci*" -o -iname "*connsys*" -o -iname "*vpu*" -o -iname "*mdp*" -o -iname "*ged*" -o -iname "*ssmr*" -o -iname "*mobile_log*" \) -print 2>/dev/null; fi; done'
run_capture users shell pm list users
run_capture settings_device_provisioned shell settings get global device_provisioned
run_capture settings_user_setup shell settings get secure user_setup_complete

timestamp_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
cat > "$OUTPUT/metadata.tsv" <<EOF
test_id\t$TEST_ID
serial\t$SERIAL
timestamp_utc\t$timestamp_utc
scope\tread-only MediaTek Android CVE surface triage
candidates\tCVE-2022-20053,CVE-2022-20054,CVE-2022-20062,CVE-2022-20067,CVE-2022-20069,CVE-2022-20073,CVE-2022-20055
mutations\tNONE
device_node_open\tNOT_EXECUTED
ioctl\tNOT_EXECUTED
modem_or_at_traffic\tNOT_EXECUTED
kernel_trigger\tNOT_EXECUTED
boot_or_partition_write\tNOT_EXECUTED
EOF

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Read-only MediaTek CVE surface captured in %s\n' "$OUTPUT"
