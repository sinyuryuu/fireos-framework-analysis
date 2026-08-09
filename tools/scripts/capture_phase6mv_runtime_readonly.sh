#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  capture_phase6mv_runtime_readonly.sh --serial SERIAL --output DIR [--dry-run]

Read-only runtime capture. The output directory must not already exist.
EOF
}

SERIAL=""
OUTPUT=""
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --serial) [[ $# -ge 2 ]] || { usage >&2; exit 2; }; SERIAL="$2"; shift 2 ;;
    --output) [[ $# -ge 2 ]] || { usage >&2; exit 2; }; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done
[[ -n "$SERIAL" && -n "$OUTPUT" ]] || { usage >&2; exit 2; }

COMMANDS=(
  "adb -s $SERIAL get-state"
  "adb -s $SERIAL shell getprop"
  "adb -s $SERIAL shell getenforce"
  "adb -s $SERIAL shell id"
  "adb -s $SERIAL shell cmd activity get-current-user"
  "adb -s $SERIAL shell pm list users"
  "adb -s $SERIAL shell cmd package resolve-activity --brief --user 0 -a android.intent.action.MAIN -c android.intent.category.HOME"
  "adb -s $SERIAL shell cmd package query-activities --brief --user 0 -a android.intent.action.MAIN -c android.intent.category.HOME"
  "adb -s $SERIAL shell dumpsys package preferred-xml"
  "adb -s $SERIAL shell dumpsys package com.amazon.firelauncher"
  "adb -s $SERIAL shell dumpsys activity activities"
  "adb -s $SERIAL shell dumpsys activity recents"
  "adb -s $SERIAL shell dumpsys window windows"
  "adb -s $SERIAL shell dumpsys device_policy"
  "adb -s $SERIAL shell dumpsys role"
  "adb -s $SERIAL shell service list"
  "adb -s $SERIAL shell cmd overlay list"
  "adb -s $SERIAL shell settings list system"
  "adb -s $SERIAL shell settings list secure"
  "adb -s $SERIAL shell settings list global"
  "adb -s $SERIAL shell appops get com.amazon.firelauncher"
  "adb -s $SERIAL shell appops get com.microsoft.launcher"
  "adb -s $SERIAL shell service check amazonpackagemanager"
  "adb -s $SERIAL shell service check amazonactivitymanager"
  "adb -s $SERIAL shell service check amazonwindowmanager"
  "adb -s $SERIAL shell service check amazondevicepolicymanager"
  "adb -s $SERIAL shell service check amazonaccessibilitymanager"
  "adb -s $SERIAL shell service check amazonusermanagerservice"
  "adb -s $SERIAL shell service check amazonprofileservice"
)

if [[ "$DRY_RUN" -eq 1 ]]; then
  printf 'schema=phase6mv-runtime-readonly-v1\nserial=%s\noutput=%s\n' "$SERIAL" "$OUTPUT"
  printf 'device_contacted=false\nmutation=false\nbinder_transaction=false\nreboot=false\ncommands:\n'
  printf '  %s\n' "${COMMANDS[@]}"
  exit 0
fi

if [[ -e "$OUTPUT" ]]; then
  printf 'refusing to overwrite existing output: %s\n' "$OUTPUT" >&2
  exit 1
fi
DEVICE_LINES="$(adb devices | awk -v serial="$SERIAL" '$1 == serial {print $1 "\t" $2}')"
[[ "$DEVICE_LINES" == "$SERIAL"$'\t'device ]] || {
  printf 'serial is not the authorized connected device: %s\n' "$SERIAL" >&2
  adb devices -l >&2 || true
  exit 1
}
mkdir -p "$OUTPUT"
printf '%s\n' \
  'schema=phase6mv-runtime-readonly-v1' \
  "serial=$SERIAL" \
  "timestamp_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  'device_contacted=true' 'mutation=false' 'binder_transaction=false' 'reboot=false' \
  > "$OUTPUT/metadata.txt"

run_capture() {
  local name="$1"
  shift
  "$@" > "$OUTPUT/$name.stdout.txt" 2> "$OUTPUT/$name.stderr.txt" || true
}
run_capture adb_get_state adb -s "$SERIAL" get-state
run_capture getprop adb -s "$SERIAL" shell getprop
run_capture selinux adb -s "$SERIAL" shell getenforce
run_capture shell_id adb -s "$SERIAL" shell id
run_capture current_user adb -s "$SERIAL" shell cmd activity get-current-user
run_capture users adb -s "$SERIAL" shell pm list users
run_capture home_resolve adb -s "$SERIAL" shell cmd package resolve-activity --brief --user 0 -a android.intent.action.MAIN -c android.intent.category.HOME
run_capture home_candidates adb -s "$SERIAL" shell cmd package query-activities --brief --user 0 -a android.intent.action.MAIN -c android.intent.category.HOME
run_capture preferred_xml adb -s "$SERIAL" shell dumpsys package preferred-xml
run_capture firelauncher_package adb -s "$SERIAL" shell dumpsys package com.amazon.firelauncher
run_capture activity_activities adb -s "$SERIAL" shell dumpsys activity activities
run_capture activity_recents adb -s "$SERIAL" shell dumpsys activity recents
run_capture window_windows adb -s "$SERIAL" shell dumpsys window windows
run_capture device_policy adb -s "$SERIAL" shell dumpsys device_policy
run_capture role adb -s "$SERIAL" shell dumpsys role
run_capture service_list adb -s "$SERIAL" shell service list
run_capture overlay_list adb -s "$SERIAL" shell cmd overlay list
run_capture settings_system adb -s "$SERIAL" shell settings list system
run_capture settings_secure adb -s "$SERIAL" shell settings list secure
run_capture settings_global adb -s "$SERIAL" shell settings list global
run_capture appops_firelauncher adb -s "$SERIAL" shell appops get com.amazon.firelauncher
run_capture appops_microsoft_launcher adb -s "$SERIAL" shell appops get com.microsoft.launcher
run_capture service_amazonpackagemanager adb -s "$SERIAL" shell service check amazonpackagemanager
run_capture service_amazonactivitymanager adb -s "$SERIAL" shell service check amazonactivitymanager
run_capture service_amazonwindowmanager adb -s "$SERIAL" shell service check amazonwindowmanager
run_capture service_amazondevicepolicymanager adb -s "$SERIAL" shell service check amazondevicepolicymanager
run_capture service_amazonaccessibilitymanager adb -s "$SERIAL" shell service check amazonaccessibilitymanager
run_capture service_amazonusermanagerservice adb -s "$SERIAL" shell service check amazonusermanagerservice
run_capture service_amazonprofileservice adb -s "$SERIAL" shell service check amazonprofileservice

if command -v sha256sum >/dev/null 2>&1; then
  (cd "$OUTPUT" && sha256sum -- * > sha256sums.txt)
else
  (cd "$OUTPUT" && shasum -a 256 -- * > sha256sums.txt)
fi
printf 'schema=phase6mv-runtime-readonly-v1\nserial=%s\noutput=%s\ndevice_contacted=true\nmutation=false\nbinder_transaction=false\nreboot=false\nsha256_manifest=%s/sha256sums.txt\n' "$SERIAL" "$OUTPUT" "$OUTPUT"
