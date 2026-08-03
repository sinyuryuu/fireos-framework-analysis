#!/usr/bin/env bash
# Capture a read-only pre/post mutation snapshot for Fire OS research.
# This script never changes device state. It requires an explicit serial and
# refuses to reuse an existing output directory.

set -u

SERIAL=""
TEST_ID=""
OUTPUT=""
DRY_RUN=0

usage() {
    cat <<'EOF'
Usage:
  capture_mutation_snapshot.sh --serial SERIAL --test-id TEST-ID --output DIR [--dry-run]

The script captures read-only state and writes a restore.sh template. It does
not execute restore commands or any state-changing command.
EOF
}

fail() {
    echo "ERROR: $*" >&2
    exit 2
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --serial)
            [ "$#" -ge 2 ] || fail "--serial requires a value"
            SERIAL="$2"
            shift 2
            ;;
        --test-id)
            [ "$#" -ge 2 ] || fail "--test-id requires a value"
            TEST_ID="$2"
            shift 2
            ;;
        --output)
            [ "$#" -ge 2 ] || fail "--output requires a value"
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
            fail "unknown argument: $1"
            ;;
    esac
done

[ -n "$SERIAL" ] || fail "an explicit --serial is required"
[ -n "$TEST_ID" ] || fail "an explicit --test-id is required"
[ -n "$OUTPUT" ] || fail "an explicit --output is required"

ADB=(adb -s "$SERIAL")

commands=(
    "${ADB[*]} devices -l"
    "${ADB[*]} shell getprop ro.build.fingerprint"
    "${ADB[*]} shell getprop ro.build.version.incremental"
    "${ADB[*]} shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0"
    "${ADB[*]} shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0"
    "${ADB[*]} shell dumpsys package preferred-activities"
    "${ADB[*]} shell dumpsys package com.amazon.firelauncher"
    "${ADB[*]} shell dumpsys activity activities"
    "${ADB[*]} shell dumpsys activity recents"
    "${ADB[*]} shell dumpsys window windows"
    "${ADB[*]} shell dumpsys input"
    "${ADB[*]} shell settings list secure"
    "${ADB[*]} shell settings list global"
    "${ADB[*]} shell settings list system"
    "${ADB[*]} shell device_config list"
    "${ADB[*]} shell cmd overlay list"
    "${ADB[*]} shell appops get com.amazon.firelauncher"
    "${ADB[*]} shell appops get com.microsoft.launcher"
)

if [ "$DRY_RUN" -eq 1 ]; then
    printf '%s\n' "DRY-RUN: no device command will execute; planned read-only commands:"
    printf '  %s\n' "${commands[@]}"
    printf '%s\n' "DRY-RUN: restore template would be written to $OUTPUT/restore.sh"
    exit 0
fi

case "$OUTPUT" in
    /|.|..|"" ) fail "refusing unsafe output directory: $OUTPUT" ;;
esac
[ ! -e "$OUTPUT" ] || fail "output directory already exists; refusing to overwrite: $OUTPUT"
mkdir -p "$OUTPUT/before"

printf 'test_id=%s\nserial=%s\ntimestamp_utc=%s\n' \
    "$TEST_ID" "$SERIAL" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.txt"
printf '%s\n' "${commands[@]}" > "$OUTPUT/commands.txt"

run_capture() {
    local label="$1"
    shift
    local base="$OUTPUT/before/$label"
    {
        printf 'command: '
        printf '%q ' "$@"
        printf '\n'
    } > "$base.command.txt"
    "$@" > "$base.stdout.txt" 2> "$base.stderr.txt"
    printf '%s\n' "$?" > "$base.exit_code.txt"
}

run_capture devices "${ADB[@]}" devices -l
grep -Eq "^${SERIAL}[[:space:]].*\bdevice\b" "$OUTPUT/before/devices.stdout.txt" || \
    fail "serial is not connected in device state; see $OUTPUT/before/devices.stdout.txt"

run_capture fingerprint "${ADB[@]}" shell getprop ro.build.fingerprint
run_capture incremental "${ADB[@]}" shell getprop ro.build.version.incremental
run_capture home_resolve "${ADB[@]}" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_capture home_candidates "${ADB[@]}" shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
run_capture preferred_activities "${ADB[@]}" shell dumpsys package preferred-activities
run_capture firelauncher_package "${ADB[@]}" shell dumpsys package com.amazon.firelauncher
run_capture activity "${ADB[@]}" shell dumpsys activity activities
run_capture recents "${ADB[@]}" shell dumpsys activity recents
run_capture windows "${ADB[@]}" shell dumpsys window windows
run_capture input "${ADB[@]}" shell dumpsys input
run_capture settings_secure "${ADB[@]}" shell settings list secure
run_capture settings_global "${ADB[@]}" shell settings list global
run_capture settings_system "${ADB[@]}" shell settings list system
run_capture device_config "${ADB[@]}" shell device_config list
run_capture overlays "${ADB[@]}" shell cmd overlay list
run_capture firelauncher_appops "${ADB[@]}" shell appops get com.amazon.firelauncher
run_capture microsoft_appops "${ADB[@]}" shell appops get com.microsoft.launcher

cat > "$OUTPUT/restore.sh" <<'EOF'
#!/usr/bin/env bash
# Generated restore template. It is intentionally not executable by default.
# Fill in only commands corresponding to the mutation recorded in metadata.
# Verify the before/after snapshots before running any command.
set -u
: "${SERIAL:?Set SERIAL to the recorded device serial before restoring}"

# Examples for a preferred-home test (do not run unless that exact mutation
# was recorded in this test directory):
# adb -s "$SERIAL" shell cmd package set-home-activity com.amazon.firelauncher/.Launcher

# Examples for a settings key that was originally absent:
# adb -s "$SERIAL" shell settings delete global KEY

# Examples for a package state mutation:
# adb -s "$SERIAL" shell pm enable --user 0 PACKAGE

echo "Restore template only; no automatic restore command is defined."
EOF
chmod 644 "$OUTPUT/restore.sh"

find "$OUTPUT" -type f -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
cat > "$OUTPUT/result.md" <<EOF
# Read-only mutation snapshot

- Test ID: \`$TEST_ID\`
- Serial: \`$SERIAL\`
- No state-changing command was executed by this script.
- The output contains pre-state evidence and a non-executing restore template.
- SHA-256: \`sha256sums.txt\`
EOF

echo "Captured read-only mutation snapshot in $OUTPUT"
