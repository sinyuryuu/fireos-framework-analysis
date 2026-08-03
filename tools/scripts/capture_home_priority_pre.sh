#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
. "$SCRIPT_DIR/common.sh"

SERIAL=""
OUTPUT=""
DRY_RUN=0
FIRE_COMPONENT="com.amazon.firelauncher/com.amazon.firelauncher.Launcher"

usage() {
    cat <<'EOF'
Usage:
  capture_home_priority_pre.sh --serial SERIAL --output DIR [--dry-run]

Captures the read-only Phase 3A pre-state. It never installs, starts,
reboots, disables, clears, or changes a package/preferred/settings state.
EOF
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 2
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --serial) [ "$#" -ge 2 ] || fail '--serial requires a value'; SERIAL="$2"; shift 2 ;;
        --output) [ "$#" -ge 2 ] || fail '--output requires a value'; OUTPUT="$2"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) fail "unknown argument: $1" ;;
    esac
done

[ -n "$SERIAL" ] || fail '--serial is required'
[ -n "$OUTPUT" ] || fail '--output is required'

if [ "$DRY_RUN" -eq 1 ]; then
    printf 'DRY-RUN: no ADB command or output directory will be created.\n'
    printf 'DRY-RUN: serial=%s output=%s\n' "$SERIAL" "$OUTPUT"
    printf 'DRY-RUN: getprop, HOME resolve/query, preferred activities, package, activity, recents, window, overlay, settings.\n'
    exit 0
fi

validate_serial "$SERIAL"
ensure_new_path "$OUTPUT"
mkdir -p "$OUTPUT/before"
: > "$OUTPUT/commands.txt"
printf 'label\tstatus\tstarted_utc\tfinished_utc\tcommand\tstdout\n' > "$OUTPUT/command-manifest.tsv"

capture_cmd() {
    local label="$1"
    shift
    local stdout_file="$OUTPUT/before/$label.stdout.txt"
    local stderr_file="$OUTPUT/before/$label.stderr.txt"
    local started finished status
    local command_text="adb -s $(quote_arg "$SERIAL") $(render_command "$@")"
    started=$(timestamp_utc)
    printf '%s\n' "$command_text" >> "$OUTPUT/commands.txt"
    set +e
    adb -s "$SERIAL" "$@" >"$stdout_file" 2>"$stderr_file"
    status=$?
    set -e
    finished=$(timestamp_utc)
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$label" "$status" "$started" "$finished" "$command_text" "$stdout_file" \
        >> "$OUTPUT/command-manifest.tsv"
}

capture_cmd devices devices -l
capture_cmd fingerprint shell getprop ro.build.fingerprint
capture_cmd incremental shell getprop ro.build.version.incremental
capture_cmd verified_boot shell getprop ro.boot.verifiedbootstate
capture_cmd home_resolve shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
capture_cmd home_query shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
capture_cmd preferred shell dumpsys package preferred-activities
capture_cmd persistent_preferred shell dumpsys package preferred-activities
capture_cmd package_firelauncher shell dumpsys package com.amazon.firelauncher
capture_cmd activity shell dumpsys activity activities
capture_cmd recents shell dumpsys activity recents
capture_cmd window shell dumpsys window windows
capture_cmd overlay shell cmd overlay list
capture_cmd settings_secure shell settings list secure
capture_cmd settings_global shell settings list global
capture_cmd settings_system shell settings list system

{
    printf '{\n'
    printf '  "test_id": "HOME-PRIORITY-PRE",\n'
    printf '  "serial": "%s",\n' "$SERIAL"
    printf '  "fire_component": "%s",\n' "$FIRE_COMPONENT"
    printf '  "captured_utc": "%s",\n' "$(timestamp_utc)"
    printf '  "read_only": true,\n'
    printf '  "state_change_executed": false\n'
    printf '}\n'
} > "$OUTPUT/metadata.json"

cat > "$OUTPUT/restore.sh" <<EOF
#!/usr/bin/env bash
set -u
adb -s '$SERIAL' shell cmd package set-home-activity '$FIRE_COMPONENT'
EOF
chmod +x "$OUTPUT/restore.sh"
write_sha256_manifest "$OUTPUT" "$OUTPUT/sha256sums.txt"
printf 'Read-only Phase 3A pre-snapshot captured at %s\n' "$OUTPUT"
