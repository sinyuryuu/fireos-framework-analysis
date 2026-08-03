#!/usr/bin/env bash
# Run exactly one approved MTK-SU CMDQ control test.
#
# Scope is intentionally narrow: push the already archived mtk-su64 payload to
# a new /data/local/tmp directory, execute it once with a fixed diagnostic
# input, and remove only that directory.  This script does not run Magisk,
# remount anything, change Android settings, access partitions, reboot, or run
# any post-exploitation command.

set -Eeuo pipefail

SERIAL=""
OUTPUT=""
APK="artifacts/phase5/mtk-easy-su-audit-20260803/mtk-easy-su-v2.2.1-KoModed2.apk"
DRY_RUN=0
ADB_BIN="${ADB_BIN:-adb}"
TEST_ID="MTK-SU-CMDQ-T03"
REMOTE_DIR="/data/local/tmp/${TEST_ID}"
EXPECTED_HASH="328632e853ff6427af9f35cb83a91d9e960f35d01188ee66d46ae9c7ce7c7827"
LOGCAT_PID=""
DEVICE_AVAILABLE=0
REMOTE_CREATED=0
CLEANED=0

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 2
}

usage() {
  cat <<'EOF'
Usage:
  run_mtk_su_cmdq_t03.sh --serial SERIAL --output DIR [--apk APK] [--dry-run]

This is the single approved MTK-SU-CMDQ-T03 control test.  It requires an
explicit serial and refuses to overwrite an existing evidence directory.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --apk) [ "$#" -ge 2 ] || die '--apk requires a value'; APK="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in
  /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;;
esac

command -v "$ADB_BIN" >/dev/null 2>&1 || die "adb not found: $ADB_BIN"
command -v python3 >/dev/null 2>&1 || die 'python3 is required for the bounded one-shot runner'
command -v unzip >/dev/null 2>&1 || die 'unzip is required to extract the archived asset'
command -v shasum >/dev/null 2>&1 || die 'shasum is required to verify the payload'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: validate adb serial %q is in device state\n' "$SERIAL"
  printf 'DRY-RUN: extract assets/mtk-su64 from %q\n' "$APK"
  printf 'DRY-RUN: verify SHA-256 %s\n' "$EXPECTED_HASH"
  printf 'DRY-RUN: adb -s %q push PAYLOAD %s/mtk-su64\n' "$SERIAL" "$REMOTE_DIR"
  printf 'DRY-RUN: adb -s %q shell chmod 700 %s/mtk-su64\n' "$SERIAL" "$REMOTE_DIR"
  printf 'DRY-RUN: execute %s/mtk-su64 -v once with id/getenforce/cat /proc/version/exit\n' "$REMOTE_DIR"
  printf 'DRY-RUN: remove only %s; no reboot, remount, partition, settings, or Magisk operation\n' "$REMOTE_DIR"
  exit 0
fi

[ -f "$APK" ] || die "APK not found: $APK"
[ ! -e "$OUTPUT" ] || die "output directory already exists; refusing to overwrite: $OUTPUT"
mkdir -p "$OUTPUT/before" "$OUTPUT/host" "$OUTPUT/exec" "$OUTPUT/after-exec" "$OUTPUT/rollback" "$OUTPUT/after-rollback" "$OUTPUT/logcat"
OUTPUT="$(cd "$OUTPUT" && pwd)"

timestamp_utc() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

run_capture() {
  local label="$1"
  shift
  local base="$OUTPUT/$label"
  mkdir -p "$(dirname "$base")"
  {
    printf 'timestamp_utc=%s\n' "$(timestamp_utc)"
    printf 'command='
    printf '%q ' "$@"
    printf '\n'
  } > "$base.command.txt"
  set +e
  "$@" > "$base.stdout.txt" 2> "$base.stderr.txt"
  local status=$?
  set -e
  printf '%s\n' "$status" > "$base.exit_code.txt"
  return 0
}

run_host_capture() {
  local label="$1"
  shift
  run_capture "host/$label" "$@"
}

capture_device_state() {
  local prefix="$1"
  run_capture "$prefix/adb_state" "$ADB_BIN" -s "$SERIAL" get-state
  run_capture "$prefix/getprop" "$ADB_BIN" -s "$SERIAL" shell getprop
  run_capture "$prefix/id" "$ADB_BIN" -s "$SERIAL" shell id
  run_capture "$prefix/selinux" "$ADB_BIN" -s "$SERIAL" shell getenforce
  run_capture "$prefix/shell_context" "$ADB_BIN" -s "$SERIAL" shell cat /proc/self/attr/current
  run_capture "$prefix/kernel" "$ADB_BIN" -s "$SERIAL" shell cat /proc/version
  run_capture "$prefix/boot_state" "$ADB_BIN" -s "$SERIAL" shell 'getprop ro.boot.flash.locked; getprop ro.boot.verifiedbootstate; getprop ro.boot.mode'
  run_capture "$prefix/home_resolver" "$ADB_BIN" -s "$SERIAL" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
  run_capture "$prefix/home_candidates" "$ADB_BIN" -s "$SERIAL" shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME
  run_capture "$prefix/preferred_xml" "$ADB_BIN" -s "$SERIAL" shell dumpsys package preferred-xml
  run_capture "$prefix/firelauncher_path" "$ADB_BIN" -s "$SERIAL" shell pm path com.amazon.firelauncher
  run_capture "$prefix/firelauncher_package" "$ADB_BIN" -s "$SERIAL" shell dumpsys package com.amazon.firelauncher
  run_capture "$prefix/activity" "$ADB_BIN" -s "$SERIAL" shell dumpsys activity activities
  run_capture "$prefix/window" "$ADB_BIN" -s "$SERIAL" shell dumpsys window windows
  run_capture "$prefix/cmdq_node" "$ADB_BIN" -s "$SERIAL" shell ls -lZ /dev/mtk_cmdq
}

record_metadata() {
  printf 'test_id=%s\nserial=%s\noperation=approved_single_bare_mtk_su64_cmdq_control_test\nstarted_utc=%s\n' \
    "$TEST_ID" "$SERIAL" "$(timestamp_utc)" > "$OUTPUT/metadata.tsv"
  printf 'source_apk=%s\nexpected_payload_sha256=%s\nremote_dir=%s\n' \
    "$APK" "$EXPECTED_HASH" "$REMOTE_DIR" >> "$OUTPUT/metadata.tsv"
  printf '%s\n' \
    "adb -s $SERIAL get-state" \
    "adb -s $SERIAL shell mkdir -p $REMOTE_DIR" \
    "adb -s $SERIAL push host/mtk-su64 $REMOTE_DIR/mtk-su64" \
    "adb -s $SERIAL shell chmod 700 $REMOTE_DIR/mtk-su64" \
    "adb -s $SERIAL shell 'cd $REMOTE_DIR && ./mtk-su64 -v' < id/getenforce/cat_proc_version/exit" \
    "adb -s $SERIAL shell rm -rf $REMOTE_DIR" \
    > "$OUTPUT/commands.txt"
}

stop_logcat() {
  if [ -n "$LOGCAT_PID" ] && kill -0 "$LOGCAT_PID" 2>/dev/null; then
    kill "$LOGCAT_PID" 2>/dev/null || true
    wait "$LOGCAT_PID" 2>/dev/null || true
  fi
  LOGCAT_PID=""
}

trap stop_logcat EXIT

record_metadata

run_capture before/adb_state "$ADB_BIN" -s "$SERIAL" get-state
state=$(tr -d '\r\n' < "$OUTPUT/before/adb_state.stdout.txt")
[ "$state" = 'device' ] || die "serial is not in device state: $state"

capture_device_state before

run_host_capture source_apk_sha256 shasum -a 256 "$APK"
run_host_capture source_apk_file file "$APK"

printf 'timestamp_utc=%s\ncommand=unzip -p %q assets/mtk-su64\n' "$(timestamp_utc)" "$APK" > "$OUTPUT/host/extract.command.txt"
set +e
unzip -p "$APK" assets/mtk-su64 > "$OUTPUT/host/mtk-su64" 2> "$OUTPUT/host/extract.stderr.txt"
extract_status=$?
set -e
printf '%s\n' "$extract_status" > "$OUTPUT/host/extract.exit_code.txt"
[ "$extract_status" -eq 0 ] || die "could not extract assets/mtk-su64"

run_host_capture extracted_payload_file file "$OUTPUT/host/mtk-su64"
run_host_capture extracted_payload_sha256 shasum -a 256 "$OUTPUT/host/mtk-su64"
actual_hash=$(shasum -a 256 "$OUTPUT/host/mtk-su64" | awk '{print $1}')
printf '%s\n' "$EXPECTED_HASH" > "$OUTPUT/host/expected_payload_sha256.txt"
if [ "$actual_hash" != "$EXPECTED_HASH" ]; then
  printf 'actual=%s\nexpected=%s\n' "$actual_hash" "$EXPECTED_HASH" > "$OUTPUT/host/hash-mismatch.txt"
  die 'payload SHA-256 did not match the approved artifact'
fi

if command -v readelf >/dev/null 2>&1; then
  run_host_capture extracted_payload_readelf readelf -h "$OUTPUT/host/mtk-su64"
fi

run_capture before/logcat_clear "$ADB_BIN" -s "$SERIAL" logcat -c
set +e
"$ADB_BIN" -s "$SERIAL" logcat -b all -v threadtime > "$OUTPUT/logcat/live.stdout.txt" 2> "$OUTPUT/logcat/live.stderr.txt" &
LOGCAT_PID=$!
set -e
printf 'timestamp_utc=%s\ncommand=' "$(timestamp_utc)" > "$OUTPUT/logcat/live.command.txt"
printf '%q ' "$ADB_BIN" -s "$SERIAL" logcat -b all -v threadtime >> "$OUTPUT/logcat/live.command.txt"
printf '\n' >> "$OUTPUT/logcat/live.command.txt"
printf '%s\n' "$LOGCAT_PID" > "$OUTPUT/logcat/live.pid.txt"

run_capture push_mkdir "$ADB_BIN" -s "$SERIAL" shell mkdir -p "$REMOTE_DIR"
run_capture push_payload "$ADB_BIN" -s "$SERIAL" push "$OUTPUT/host/mtk-su64" "$REMOTE_DIR/mtk-su64"
REMOTE_CREATED=1
run_capture remote_chmod "$ADB_BIN" -s "$SERIAL" shell chmod 700 "$REMOTE_DIR/mtk-su64"
run_capture remote_listing "$ADB_BIN" -s "$SERIAL" shell ls -lZ "$REMOTE_DIR/mtk-su64"
run_capture remote_sha256 "$ADB_BIN" -s "$SERIAL" shell sha256sum "$REMOTE_DIR/mtk-su64"

printf 'id\ngetenforce\ncat /proc/version\nexit\n' > "$OUTPUT/exec/input.txt"
printf 'cd %s && ./mtk-su64 -v\n' "$REMOTE_DIR" > "$OUTPUT/exec/remote_command.txt"
printf 'timestamp_utc=%s\ncommand=python3 bounded adb runner\n' "$(timestamp_utc)" > "$OUTPUT/exec/runner.command.txt"

set +e
python3 - "$ADB_BIN" "$SERIAL" "$REMOTE_DIR" "$OUTPUT/exec/mtk-su64.stdout.txt" "$OUTPUT/exec/mtk-su64.stderr.txt" <<'PY'
import os
import signal
import subprocess
import sys

adb, serial, remote_dir, stdout_path, stderr_path = sys.argv[1:]
command = [adb, "-s", serial, "shell", f"cd {remote_dir} && ./mtk-su64 -v"]
payload = b"id\ngetenforce\ncat /proc/version\nexit\n"
code = 125
with open(stdout_path, "wb") as stdout, open(stderr_path, "wb") as stderr:
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=stdout,
        stderr=stderr,
        start_new_session=True,
    )
    try:
        process.communicate(payload, timeout=45)
        code = process.returncode
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()
        code = 124
sys.exit(code if code is not None else 125)
PY
exec_status=$?
set -e
printf '%s\n' "$exec_status" > "$OUTPUT/exec/exit_code.txt"
printf 'timeout_seconds=45\n' > "$OUTPUT/exec/timeout.txt"

run_capture after-exec/adb_state "$ADB_BIN" -s "$SERIAL" get-state
state=$(tr -d '\r\n' < "$OUTPUT/after-exec/adb_state.stdout.txt")
if [ "$state" != 'device' ]; then
  {
    printf 'start_utc=%s\n' "$(timestamp_utc)"
    for attempt in $(seq 1 90); do
      polled=$("$ADB_BIN" -s "$SERIAL" get-state 2>&1) || true
      printf '%s\tattempt=%s\tstate=%s\n' "$(timestamp_utc)" "$attempt" "$polled"
      if [ "$polled" = 'device' ]; then
        DEVICE_AVAILABLE=1
        break
      fi
      sleep 1
    done
    printf 'end_utc=%s\n' "$(timestamp_utc)"
  } > "$OUTPUT/after-exec/device-recovery-poll.txt"
  if [ "$DEVICE_AVAILABLE" -ne 1 ]; then
    state_after_poll=$("$ADB_BIN" -s "$SERIAL" get-state 2>&1) || true
    if [ "$state_after_poll" = 'device' ]; then DEVICE_AVAILABLE=1; fi
  fi
else
  DEVICE_AVAILABLE=1
fi

if [ "$DEVICE_AVAILABLE" -eq 1 ]; then
  capture_device_state after-exec
  run_capture rollback/remove_temp "$ADB_BIN" -s "$SERIAL" shell rm -rf "$REMOTE_DIR"
  CLEANED=1
  run_capture rollback/remote_listing_after_remove "$ADB_BIN" -s "$SERIAL" shell ls -ld "$REMOTE_DIR"
  capture_device_state after-rollback
else
  printf 'ADB did not return to device state; remote cleanup was not attempted.\n' > "$OUTPUT/rollback/cleanup-pending.txt"
fi

stop_logcat
if [ "$DEVICE_AVAILABLE" -eq 1 ]; then
  run_capture logcat/final_dump "$ADB_BIN" -s "$SERIAL" logcat -d -b all -v threadtime
fi

root_marker='not observed'
if grep -Eq 'uid=0\(root\)|uid=0([^0-9]|$)' "$OUTPUT/exec/mtk-su64.stdout.txt" 2>/dev/null; then
  root_marker='uid=0 marker observed in exploit stdout'
fi

if [ "$DEVICE_AVAILABLE" -eq 1 ]; then
  adb_observation='device state'
else
  adb_observation='not restored to device state during bounded wait'
fi
if [ "$CLEANED" -eq 1 ]; then
  cleanup_observation='completed'
else
  cleanup_observation='not attempted; see rollback/cleanup-pending.txt'
fi

{
  printf '# %s result\n\n' "$TEST_ID"
  printf -- '- Serial: %s\n' "$SERIAL"
  printf -- '- Approved scope: one bare mtk-su64 -v execution using the archived payload.\n'
  printf -- '- Payload SHA-256: %s (expected %s).\n' "$actual_hash" "$EXPECTED_HASH"
  printf -- '- Exploit runner exit code: %s.\n' "$exec_status"
  printf -- '- Root marker: **%s**.\n' "$root_marker"
  printf -- '- ADB after execution/observation: **%s**.\n' "$adb_observation"
  printf -- '- Temporary directory cleanup: **%s**.\n' "$cleanup_observation"
  printf '\nThe raw exploit stdout/stderr, fixed input, command records, logcat, before/\n'
  printf 'after snapshots, and SHA-256 manifest are retained in this directory.  No\n'
  printf 'Magisk command, remount, setting mutation, package mutation, reboot, fastboot\n'
  printf 'operation, partition access, or post-exploitation command was executed.\n'
} > "$OUTPUT/result.md"

printf 'finished_utc=%s\nexec_exit_code=%s\nadb_available=%s\nremote_cleanup=%s\nroot_marker=%s\n' \
  "$(timestamp_utc)" "$exec_status" "$DEVICE_AVAILABLE" "$CLEANED" "$root_marker" >> "$OUTPUT/metadata.tsv"

(cd "$OUTPUT" && find . -type f ! -name sha256sums.txt -print | sort | while IFS= read -r file; do shasum -a 256 "$file"; done) > "$OUTPUT/sha256sums.txt"
printf 'Evidence written to %s\n' "$OUTPUT"
