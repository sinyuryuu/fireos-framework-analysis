#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
COMPONENT=''
USER_ID='0'
OUTPUT=''
PACKAGE_TOOL='pm'
PACKAGE_COMMAND=(pm)
APPROVE_STATE_CHANGE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: test_component_disable.sh --serial SERIAL --component PACKAGE/CLASS --output DIR
       [--user USER_ID] [--command pm|cmd] [--approve-state-change] [--dry-run]

Temporarily disables one component, captures HOME behavior, restores that
component to Android's default state, then sends Home again. The experiment
does not clear data, uninstall, suspend, reboot or modify Settings. Live
execution requires an interactive approval phrase.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial)
      [ "$#" -ge 2 ] || die '--serial requires a value'
      SERIAL="$2"; shift 2 ;;
    --component)
      [ "$#" -ge 2 ] || die '--component requires a value'
      COMPONENT="$2"; shift 2 ;;
    --user)
      [ "$#" -ge 2 ] || die '--user requires a value'
      USER_ID="$2"; shift 2 ;;
    --output)
      [ "$#" -ge 2 ] || die '--output requires a path'
      OUTPUT="$2"; shift 2 ;;
    --command)
      [ "$#" -ge 2 ] || die '--command requires a value'
      PACKAGE_TOOL="$2"; shift 2 ;;
    --approve-state-change) APPROVE_STATE_CHANGE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$COMPONENT" ] || die '--component is required'
[ -n "$OUTPUT" ] || die '--output is required'
printf '%s' "$USER_ID" | grep -Eq '^[0-9]+$' || die '--user must be a numeric user ID'
printf '%s' "$COMPONENT" | grep -Eq '^[A-Za-z0-9_.]+/[A-Za-z0-9_.$]+$' || die '--component must match PACKAGE/CLASS'
case "$PACKAGE_TOOL" in
  pm) PACKAGE_COMMAND=(pm) ;;
  cmd) PACKAGE_COMMAND=(cmd package) ;;
  *) die '--command must be pm or cmd' ;;
esac

PACKAGE="${COMPONENT%%/*}"

print_plan() {
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: serial=%s component=%s package=%s user=%s command=%s output=%s\n' \
    "$SERIAL" "$COMPONENT" "$PACKAGE" "$USER_ID" "${PACKAGE_COMMAND[*]}" "$OUTPUT"
  printf "DRY-RUN: read-only snapshots: adb -s '%s' shell dumpsys package '%s'\n" "$SERIAL" "$PACKAGE"
  printf "DRY-RUN: gated component disable: adb -s '%s' shell %s disable-user --user '%s' '%s'\n" \
    "$SERIAL" "${PACKAGE_COMMAND[*]}" "$USER_ID" "$COMPONENT"
  printf "DRY-RUN: gated Home event while component state is changed: adb -s '%s' shell input keyevent 3\n" "$SERIAL"
  printf "DRY-RUN: gated restore: adb -s '%s' shell %s default-state --user '%s' '%s'\n" \
    "$SERIAL" "${PACKAGE_COMMAND[*]}" "$USER_ID" "$COMPONENT"
  printf 'DRY-RUN: before/after/final snapshots, summary and SHA-256 manifest would be written under %s\n' "$OUTPUT"
}

if [ "$DRY_RUN" -eq 1 ]; then
  print_plan
  exit 0
fi

validate_serial "$SERIAL"
ensure_new_path "$OUTPUT"
mkdir -p "$OUTPUT"
MANIFEST="$OUTPUT/command_manifest.tsv"
printf 'label\tstatus\tstarted_utc\tfinished_utc\tcommand\toutput\n' > "$MANIFEST"
HARD_FAILURES=0
LAST_STATUS=0
ADB_SERIAL="$SERIAL"

[ "$APPROVE_STATE_CHANGE" -eq 1 ] || die 'live component test requires --approve-state-change and the interactive approval phrase'
printf 'This test changes one component state temporarily, sends Home, restores the component, and sends Home again.\n'
printf 'Type APPROVE COMPONENT %s to continue: ' "$COMPONENT"
read -r approval
[ "$approval" = "APPROVE COMPONENT $COMPONENT" ] || die 'approval phrase did not match; no state-changing command was executed'

printf 'test_id=COMPONENT-DISABLE-%s\nserial=%s\ncomponent=%s\npackage=%s\nuser=%s\ncommand=%s\nstarted_utc=%s\n' \
  "$(timestamp_id)" "$SERIAL" "$COMPONENT" "$PACKAGE" "$USER_ID" "${PACKAGE_COMMAND[*]}" "$(timestamp_utc)" > "$OUTPUT/test_metadata.txt"

capture_state() {
  local phase="$1"
  run_adb_capture "${phase}_package" no "$OUTPUT/${phase}_package.txt" shell dumpsys package "$PACKAGE"
  run_adb_capture "${phase}_disabled_packages" no "$OUTPUT/${phase}_disabled_packages.txt" shell pm list packages -d
  run_adb_capture "${phase}_home_resolve" no "$OUTPUT/${phase}_home_resolve.txt" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user "$USER_ID"
  run_adb_capture "${phase}_activity" no "$OUTPUT/${phase}_activity.txt" shell dumpsys activity activities
  run_adb_capture "${phase}_window" no "$OUTPUT/${phase}_window.txt" shell dumpsys window windows
}

capture_state before
run_adb_capture 'disable_component' yes "$OUTPUT/disable_component.txt" shell "${PACKAGE_COMMAND[@]}" disable-user --user "$USER_ID" "$COMPONENT"
disable_status="$LAST_STATUS"
printf 'disable_status=%s\n' "$disable_status" >> "$OUTPUT/test_metadata.txt"
capture_state after_disable

run_adb_capture 'home_while_component_state' yes "$OUTPUT/home_while_component_state.txt" shell input keyevent 3
home_status="$LAST_STATUS"
printf 'home_while_component_status=%s\n' "$home_status" >> "$OUTPUT/test_metadata.txt"
capture_state after_home

if [ "$disable_status" -eq 0 ]; then
  run_adb_capture 'restore_component_default_state' yes "$OUTPUT/restore_component_default_state.txt" shell "${PACKAGE_COMMAND[@]}" default-state --user "$USER_ID" "$COMPONENT"
  restore_status="$LAST_STATUS"
else
  restore_status='SKIPPED_DISABLE_REJECTED'
  printf 'restore_component_default_state was skipped because disable-user was rejected before state mutation.\n' > "$OUTPUT/restore_component_default_state.txt"
fi
printf 'restore_status=%s\n' "$restore_status" >> "$OUTPUT/test_metadata.txt"
capture_state after_restore

run_adb_capture 'home_after_restore' yes "$OUTPUT/home_after_restore.txt" shell input keyevent 3
home_restore_status="$LAST_STATUS"
printf 'home_after_restore_status=%s\nfinished_utc=%s\n' "$home_restore_status" "$(timestamp_utc)" >> "$OUTPUT/test_metadata.txt"
capture_state final

if command -v rg >/dev/null 2>&1; then
  rg -n 'enabled=|User [0-9]+:|Package \[|mResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|com\.amazon\.firelauncher|com\.microsoft\.launcher|FallbackHome' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
else
  grep -REn 'enabled=|User [0-9]+:|Package \[|mResumedActivity|topResumedActivity|mFocusedApp|mCurrentFocus|com\.amazon\.firelauncher|com\.microsoft\.launcher|FallbackHome' \
    "$OUTPUT" > "$OUTPUT/state_focus_lines.txt" || true
fi

{
  printf '# Component disable test summary\n\n'
  printf -- '- Serial: `%s`\n' "$SERIAL"
  printf -- '- Component: `%s`\n' "$COMPONENT"
  printf -- '- Package: `%s`\n' "$PACKAGE"
  printf -- '- User: `%s`\n' "$USER_ID"
  printf -- '- Disable exit status: `%s`\n' "$disable_status"
  printf -- '- Home while component state changed exit status: `%s`\n' "$home_status"
  printf -- '- Restore exit status: `%s`\n' "$restore_status"
  printf -- '- Home after restore exit status: `%s`\n' "$home_restore_status"
  printf -- '- Causal finding: `Hypothesis` until raw state and command outputs are reviewed.\n\n'
  printf '## Evidence\n\n'
  printf -- '- [Command manifest](command_manifest.tsv)\n'
  printf -- '- [State focus lines](state_focus_lines.txt)\n'
  printf -- '- [SHA-256 manifest](sha256sums.txt)\n\n'
  printf 'The final snapshot must be compared with the before snapshot before reporting restoration as successful.\n'
} > "$OUTPUT/test_summary.md"

write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"
printf 'Component disable test completed: %s\n' "$COMPONENT"
if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'Component disable test completed with %s required command failure(s); inspect %s\n' "$HARD_FAILURES" "$MANIFEST" >&2
  exit 2
fi
