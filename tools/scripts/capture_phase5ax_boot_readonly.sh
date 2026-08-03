#!/usr/bin/env bash
set -Eeuo pipefail

# Read-only Android block-device artifact probe.
# It never opens a device node for writing and never reads userdata.
# --full-boot copies only /dev/block/by-name/boot when shell permissions allow it.

SERIAL=""
OUTPUT=""
FULL_BOOT=0
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

usage() {
  cat <<'EOF'
Usage:
  capture_phase5ax_boot_readonly.sh --serial SERIAL --output DIR
  capture_phase5ax_boot_readonly.sh --serial SERIAL --output DIR --full-boot
  capture_phase5ax_boot_readonly.sh --serial SERIAL --output DIR --dry-run

The default captures only read-only metadata and 4 KiB headers for boot, lk and
recovery. --full-boot additionally copies boot to the host if the shell can read
it. No userdata path is accessed. The output directory must not already exist.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --full-boot) FULL_BOOT=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in
  /|.|..|/tmp|/var/tmp|"$PWD"|"$PWD/"*) die 'unsafe output path' ;;
esac
[ ! -e "$OUTPUT" ] || die "refusing to overwrite existing output: $OUTPUT"

if [ "$DRY_RUN" -eq 1 ]; then
  cat <<EOF
serial=$SERIAL
output=$OUTPUT
full_boot=$FULL_BOOT
read-only commands:
  adb -s $SERIAL get-state
  adb -s $SERIAL shell getprop ro.build.fingerprint
  adb -s $SERIAL shell id
  adb -s $SERIAL shell getenforce
  adb -s $SERIAL shell readlink/ls/blockdev for /dev/block/by-name/boot,lk,recovery
  adb -s $SERIAL exec-out sh -c 'dd if=/dev/block/by-name/boot bs=4096 count=1'
EOF
  if [ "$FULL_BOOT" -eq 1 ]; then
    printf '%s\n' "optional full read: adb -s SERIAL exec-out sh -c 'dd if=/dev/block/by-name/boot bs=1048576'"
  fi
  exit 0
fi

mkdir -p "$OUTPUT"
STAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'test_id\tPHASE5AX-BOOT-READONLY-20260804-01\nserial\t%s\ntimestamp_utc\t%s\nfull_boot\t%s\nread_only\ttrue\n' \
  "$SERIAL" "$STAMP" "$FULL_BOOT" > "$OUTPUT/metadata.tsv"

run_remote() {
  local name="$1"
  local command="$2"
  printf 'adb -s %q shell %q\n' "$SERIAL" "$command" > "$OUTPUT/$name.command.txt"
  set +e
  adb -s "$SERIAL" shell "$command" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
}

run_local() {
  local name="$1"
  shift
  printf 'adb -s %q ' "$SERIAL" > "$OUTPUT/$name.command.txt"
  printf '%q ' "$@" >> "$OUTPUT/$name.command.txt"
  printf '\n' >> "$OUTPUT/$name.command.txt"
  set +e
  adb -s "$SERIAL" "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
}

run_exec_out() {
  local name="$1"
  local command="$2"
  printf 'adb -s %q exec-out sh -c %q\n' "$SERIAL" "$command" > "$OUTPUT/$name.command.txt"
  set +e
  adb -s "$SERIAL" exec-out sh -c "$command" > "$OUTPUT/$name.bin" 2> "$OUTPUT/$name.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$OUTPUT/$name.exit_code.txt"
  stat -f '%z\n' "$OUTPUT/$name.bin" > "$OUTPUT/$name.observed_size.txt" 2>/dev/null || wc -c < "$OUTPUT/$name.bin" > "$OUTPUT/$name.observed_size.txt"
}

run_local device_state get-state
if [ "$(tr -d '\r\n' < "$OUTPUT/device_state.stdout.txt")" != "device" ]; then
  die "selected serial is not in device state: $SERIAL"
fi
run_remote identity 'getprop ro.build.fingerprint; getprop ro.build.version.incremental; getprop ro.boot.flash.locked; getprop ro.boot.verifiedbootstate; id; getenforce; uname -a'
run_remote partition_links 'for p in boot lk recovery; do echo "--- $p"; readlink -f /dev/block/by-name/$p; ls -lZ /dev/block/by-name/$p; blockdev --getsize64 /dev/block/by-name/$p 2>&1; done'

for part in boot lk recovery; do
  run_remote "path_$part" "readlink -f /dev/block/by-name/$part; ls -lZ /dev/block/by-name/$part; blockdev --getsize64 /dev/block/by-name/$part 2>&1"
  run_exec_out "head_$part" "dd if=/dev/block/by-name/$part bs=4096 count=1"
done

if [ "$FULL_BOOT" -eq 1 ]; then
  run_exec_out full_boot 'dd if=/dev/block/by-name/boot bs=1048576'
fi

(
  cd "$OUTPUT"
  find . -type f ! -name 'sha256sums.txt' -print0 | sort -z | xargs -0 shasum -a 256
) > "$OUTPUT/sha256sums.txt"

printf 'capture complete: %s\n' "$OUTPUT"
