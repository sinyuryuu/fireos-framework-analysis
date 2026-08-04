#!/usr/bin/env bash
set -u

# Read-only PS7331 policy/boot visibility collector.
# It deliberately contains no futex, ioctl, package mutation, settings write,
# service mutation, reboot, bootloader, remount, or partition operation.

usage() {
  printf '%s\n' "Usage: $0 --serial SERIAL --output OUTPUT [--dry-run]"
}

serial=""
output=""
dry_run=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) serial="${2:-}"; shift 2 ;;
    --output) output="${2:-}"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$serial" ] || [ -z "$output" ]; then
  usage >&2
  exit 2
fi

if [ "$dry_run" -eq 1 ]; then
  printf '%s\n' '{"dry_run":true,"host_only_collector":false,"device_mutation":false,"commands_are_read_only":true}'
  exit 0
fi

if [ -e "$output" ]; then
  printf 'refusing to overwrite existing output: %s\n' "$output" >&2
  exit 3
fi

if ! command -v adb >/dev/null 2>&1; then
  printf 'adb not found\n' >&2
  exit 4
fi

state="$(adb -s "$serial" get-state 2>/dev/null || true)"
if [ "$state" != "device" ]; then
  printf 'target is not an online adb device: %s (%s)\n' "$serial" "$state" >&2
  exit 5
fi

mkdir -p "$output"
printf 'serial=%s\ntimestamp_utc=%s\n' "$serial" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$output/metadata.txt"

run_host() {
  label="$1"; shift
  printf 'HOST %s' "$*" >> "$output/commands.txt"
  printf '\n' >> "$output/commands.txt"
  "$@" > "$output/$label.stdout.txt" 2> "$output/$label.stderr.txt"
  rc=$?
  printf '%s rc=%s\n' "$label" "$rc" >> "$output/status.txt"
  return 0
}

run_shell() {
  label="$1"
  command_text="$2"
  printf 'adb -s %s shell %s\n' "$serial" "$command_text" >> "$output/commands.txt"
  # Pass one complete command string to the device shell.  Using
  # `shell sh -c ARG` makes some Android adb versions treat `if`/`for` tokens
  # as separate argv entries instead of the command body.
  adb -s "$serial" shell "$command_text" > "$output/$label.stdout.txt" 2> "$output/$label.stderr.txt"
  rc=$?
  printf '%s rc=%s\n' "$label" "$rc" >> "$output/status.txt"
  return 0
}

: > "$output/commands.txt"
: > "$output/status.txt"

run_host serial_check adb -s "$serial" get-serialno
run_host device_state adb -s "$serial" get-state
run_shell getprop 'getprop'
run_shell selinux_mode 'getenforce'
run_shell identity 'id'
run_shell kernel_version 'cat /proc/version'
run_shell proc_cmdline 'cat /proc/cmdline'
run_shell proc_bootconfig 'cat /proc/bootconfig'
run_shell init_selinux_context 'cat /proc/1/attr/current'
run_shell kernel_visibility 'for p in /proc/sys/kernel/randomize_va_space /proc/sys/kernel/kptr_restrict /proc/sys/kernel/panic_on_oops; do echo "PATH=$p"; cat "$p" 2>&1 || true; done'
run_shell slab_visibility 'if [ -r /proc/slabinfo ]; then grep -iE "rt.?mutex|futex|task_struct|kmalloc" /proc/slabinfo; else echo PROC_SLABINFO_NOT_READABLE; fi'
run_shell kallsyms_visibility 'if [ -r /proc/kallsyms ]; then echo KALLSYMS_READABLE_METADATA_ONLY; else echo KALLSYMS_NOT_READABLE; fi'
run_shell selinux_tree 'ls -ld /sys/fs/selinux /sys/fs/selinux/policy /sys/fs/selinux/enforce /sys/fs/selinux/status 2>&1 || true; ls -l /system/etc/selinux 2>&1 || true; ls -l /vendor/etc/selinux 2>&1 || true; ls -l /odm/etc/selinux 2>&1 || true'
run_shell policy_hashes 'for p in /sys/fs/selinux/policy /system/etc/selinux/plat_and_mapping_sepolicy.cil.sha256 /vendor/etc/selinux/precompiled_sepolicy.plat_and_mapping.sha256 /vendor/etc/selinux/precompiled_sepolicy /system/etc/selinux/plat_sepolicy.cil /system/etc/selinux/rootable_plat_sepolicy.cil /vendor/etc/selinux/plat_pub_versioned.cil /vendor/etc/selinux/rootable_plat_pub_versioned.cil /vendor/etc/selinux/vendor_sepolicy.cil /vendor/etc/selinux/rootable_vendor_sepolicy.cil /odm/etc/selinux/odm_sepolicy.cil /odm/etc/selinux/rootable_odm_sepolicy.cil; do echo "PATH=$p"; if [ -e "$p" ]; then if echo "$p" | grep -q "\.sha256$"; then cat "$p" 2>&1; else sha256sum "$p" 2>&1; fi; else echo "MISSING=$p"; fi; done'
run_shell policy_properties 'getprop | grep -iE "^(\[ro\.boot|\[ro\.debuggable|\[ro\.secure|\[ro\.build|\[ro\.product|\[ro\.odm|\[ro\.vendor|\[ro\.fireos|\[sys\.boot|\[persist\.sys).*"'
run_shell recent_policy_log 'logcat -d -b all -v threadtime -t 500 2>&1 | grep -iE "init|selinux|sepolicy|verifiedboot|policy|boot.*mode"'

run_host raw_hashes shasum -a 256 "$output"/*.stdout.txt "$output"/*.stderr.txt "$output"/metadata.txt "$output"/commands.txt "$output"/status.txt
printf 'device_mutation=false\npolicy_selected=false\nboot_property_changed=false\nfastboot_invoked=false\nfutex_triggered=false\n' >> "$output/metadata.txt"
run_host final_hashes shasum -a 256 "$output"/*.stdout.txt "$output"/*.stderr.txt "$output"/metadata.txt "$output"/commands.txt "$output"/status.txt
printf 'collector_output=%s\n' "$output"
