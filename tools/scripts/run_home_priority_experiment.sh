#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
. "$SCRIPT_DIR/common.sh"

SERIAL=""
APK_DIR=""
OUTPUT_ROOT="$PROJECT_ROOT/adb/mutation-tests"
MATRIX="$PROJECT_ROOT/output/tables/home-priority-matrix.csv"
VARIANT=""
WAIT_SECONDS="120"
APPROVE_STATE_CHANGE=0
DRY_RUN=0
REUSE_PRE_SNAPSHOT=0
APPEND_MATRIX=0
HARD_FAILURES=0
LAST_STATUS=0

FIRE_COMPONENT="com.amazon.firelauncher/com.amazon.firelauncher.Launcher"
VARIANTS_FILE="$PROJECT_ROOT/tools/test-launcher/config/variants.tsv"

usage() {
    cat <<'EOF'
Usage:
  run_home_priority_experiment.sh --serial SERIAL --apk-dir DIR
      [--output-root DIR] [--matrix FILE] [--variant PACKAGE]
      [--wait-seconds SECONDS] [--approve-state-change]
      [--reuse-pre-snapshot] [--append-matrix] [--dry-run]

Installs and tests one HOME priority APK at a time. The runner creates a
read-only HOME-PRIORITY-PRE snapshot, then a separate evidence directory for
each variant. Live execution requires the explicit approval phrase. It never
disables Fire Launcher, clears Fire Launcher data, edits the deny list, or
touches system partitions.
EOF
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 2
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --serial) [ "$#" -ge 2 ] || fail '--serial requires a value'; SERIAL="$2"; shift 2 ;;
        --apk-dir) [ "$#" -ge 2 ] || fail '--apk-dir requires a value'; APK_DIR="$2"; shift 2 ;;
        --output-root) [ "$#" -ge 2 ] || fail '--output-root requires a value'; OUTPUT_ROOT="$2"; shift 2 ;;
        --matrix) [ "$#" -ge 2 ] || fail '--matrix requires a value'; MATRIX="$2"; shift 2 ;;
        --variant) [ "$#" -ge 2 ] || fail '--variant requires a value'; VARIANT="$2"; shift 2 ;;
        --wait-seconds) [ "$#" -ge 2 ] || fail '--wait-seconds requires a value'; WAIT_SECONDS="$2"; shift 2 ;;
        --approve-state-change) APPROVE_STATE_CHANGE=1; shift ;;
        --reuse-pre-snapshot) REUSE_PRE_SNAPSHOT=1; shift ;;
        --append-matrix) APPEND_MATRIX=1; shift ;;
        --dry-run) DRY_RUN=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) fail "unknown argument: $1" ;;
    esac
done

[ -n "$SERIAL" ] || fail '--serial is required'
[ -n "$APK_DIR" ] || fail '--apk-dir is required'
[ -f "$VARIANTS_FILE" ] || fail "variants file not found: $VARIANTS_FILE"
printf '%s' "$WAIT_SECONDS" | grep -Eq '^[1-9][0-9]*$' || fail '--wait-seconds must be a positive integer'

declare -a PACKAGES=()
declare -a PRIORITIES=()
while IFS=$'\t' read -r package_name priority; do
    case "$package_name" in
        ''|\#*) continue ;;
    esac
    if [ -n "$VARIANT" ] && [ "$VARIANT" != "$package_name" ]; then
        continue
    fi
    PACKAGES+=("$package_name")
    PRIORITIES+=("$priority")
done < "$VARIANTS_FILE"
[ "${#PACKAGES[@]}" -gt 0 ] || fail 'no selected variants'

if [ "$DRY_RUN" -eq 1 ]; then
    printf 'DRY-RUN: no ADB or filesystem mutation command will execute.\n'
    printf 'DRY-RUN: serial=%s apk-dir=%s output-root=%s matrix=%s wait=%ss reuse-pre=%s append-matrix=%s\n' \
        "$SERIAL" "$APK_DIR" "$OUTPUT_ROOT" "$MATRIX" "$WAIT_SECONDS" "$REUSE_PRE_SNAPSHOT" "$APPEND_MATRIX"
    printf 'DRY-RUN: read-only pre-state: getprop, resolve-activity, query-activities, preferred activities, package, activity, window, overlay, settings.\n'
    printf 'DRY-RUN: state-changing sequence per selected variant:\n'
    printf '  adb -s SERIAL install PACKAGE.apk\n'
    printf '  adb -s SERIAL shell cmd package set-home-activity PACKAGE/org.fireosresearch.home.HomeActivity\n'
    printf '  adb -s SERIAL shell input keyevent 3\n'
    printf '  adb -s SERIAL shell input keyevent 223; adb -s SERIAL shell input keyevent 224\n'
    printf '  adb -s SERIAL reboot\n'
    printf '  adb -s SERIAL shell cmd package clear-package-preferred-activities PACKAGE\n'
    printf '  adb -s SERIAL shell cmd package set-home-activity %s\n' "$FIRE_COMPONENT"
    printf '  adb -s SERIAL uninstall PACKAGE\n'
    for package_name in "${PACKAGES[@]}"; do
        printf '  variant=%s apk=%s/%s.apk\n' "$package_name" "$APK_DIR" "$package_name"
    done
    exit 0
fi

validate_serial "$SERIAL"
[ -d "$APK_DIR" ] || fail "APK directory not found: $APK_DIR"
[ -d "$(dirname -- "$OUTPUT_ROOT")" ] || fail "output root parent does not exist: $(dirname -- "$OUTPUT_ROOT")"
[ -d "$(dirname -- "$MATRIX")" ] || fail "matrix parent does not exist: $(dirname -- "$MATRIX")"
mkdir -p "$OUTPUT_ROOT"
MATRIX_HEADER=$'test_id\tpackage\tpriority\tinstall\tinitial_resolve\tset_home\tpreferred_resolve\tkeyevent\tlock_wake\treboot\treboot_resolve\tclear_preferred\trestore_fire\tuninstall\tfinal_resolve\tfinal_status\tconfidence'
if [ -e "$MATRIX" ]; then
    [ "$APPEND_MATRIX" -eq 1 ] || fail "refusing to overwrite existing matrix: $MATRIX; use --append-matrix only after verifying its header"
    [ "$(head -n 1 "$MATRIX")" = "$MATRIX_HEADER" ] || fail "existing matrix header does not match: $MATRIX"
else
    printf '%s\n' "$MATRIX_HEADER" > "$MATRIX"
fi
[ "$APPROVE_STATE_CHANGE" -eq 1 ] || fail 'live run requires --approve-state-change'

printf 'This test installs research APKs, changes ordinary HOME preference, sends Home/wake events, reboots, and restores Fire Launcher.\n'
printf 'Type APPROVE HOME-PRIORITY-PHASE3A to continue: '
read -r approval
[ "$approval" = 'APPROVE HOME-PRIORITY-PHASE3A' ] || fail 'approval phrase did not match; no mutation was executed'

PRE_DIR="$OUTPUT_ROOT/HOME-PRIORITY-PRE"
if [ -e "$PRE_DIR" ]; then
    [ "$REUSE_PRE_SNAPSHOT" -eq 1 ] || fail "refusing to overwrite pre-snapshot: $PRE_DIR; use --reuse-pre-snapshot only after verifying its fingerprint"
else
    mkdir -p "$PRE_DIR/before"
fi

capture_cmd() {
    local dir="$1"
    local label="$2"
    local required="$3"
    shift 3
    local stdout_file="$dir/$label.stdout.txt"
    local stderr_file="$dir/$label.stderr.txt"
    local command_text="adb -s $(quote_arg "$SERIAL") $(render_command "$@")"
    local started finished status
    started=$(timestamp_utc)
    printf '%s\n' "$command_text" >> "$dir/commands.txt"
    set +e
    adb -s "$SERIAL" "$@" >"$stdout_file" 2>"$stderr_file"
    status=$?
    set -e
    finished=$(timestamp_utc)
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$label" "$status" "$started" "$finished" "$command_text" "$stdout_file" \
        >> "$dir/command-manifest.tsv"
    LAST_STATUS="$status"
    if [ "$status" -ne 0 ] && [ "$required" = yes ]; then
        HARD_FAILURES=$((HARD_FAILURES + 1))
    fi
    return 0
}

host_cmd() {
    local dir="$1"
    local label="$2"
    local required="$3"
    shift 3
    capture_cmd "$dir" "$label" "$required" "$@"
}

capture_state() {
    local dir="$1"
    local prefix="$2"
    local target_package="${3:-com.amazon.firelauncher}"
    capture_cmd "$dir" "${prefix}_fingerprint" no shell getprop ro.build.fingerprint
    capture_cmd "$dir" "${prefix}_build_incremental" no shell getprop ro.build.version.incremental
    capture_cmd "$dir" "${prefix}_verified_boot" no shell getprop ro.boot.verifiedbootstate
    capture_cmd "$dir" "${prefix}_home_resolve" no shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
    capture_cmd "$dir" "${prefix}_home_query" no shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
    capture_cmd "$dir" "${prefix}_preferred" no shell dumpsys package preferred-activities
    capture_cmd "$dir" "${prefix}_package_firelauncher" no shell dumpsys package com.amazon.firelauncher
    if [ "$target_package" != com.amazon.firelauncher ]; then
        capture_cmd "$dir" "${prefix}_package_target" no shell dumpsys package "$target_package"
    fi
    capture_cmd "$dir" "${prefix}_activity" no shell dumpsys activity activities
    capture_cmd "$dir" "${prefix}_recents" no shell dumpsys activity recents
    capture_cmd "$dir" "${prefix}_window" no shell dumpsys window windows
    capture_cmd "$dir" "${prefix}_overlay" no shell cmd overlay list
    capture_cmd "$dir" "${prefix}_settings_secure" no shell settings list secure
    capture_cmd "$dir" "${prefix}_settings_global" no shell settings list global
    capture_cmd "$dir" "${prefix}_settings_system" no shell settings list system
}

write_metadata() {
    local dir="$1"
    local test_id="$2"
    local package_name="$3"
    local priority="$4"
    printf '{\n'
    printf '  "test_id": "%s",\n' "$test_id"
    printf '  "serial": "%s",\n' "$SERIAL"
    printf '  "package": "%s",\n' "$package_name"
    printf '  "declared_priority": %s,\n' "$priority"
    printf '  "fire_component": "%s",\n' "$FIRE_COMPONENT"
    printf '  "started_utc": "%s",\n' "$(timestamp_utc)"
    printf '  "risk_level": "Level 2 reversible mutation",\n'
    printf '  "forbidden_operations": ["disable Fire Launcher", "clear Fire Launcher data", "modify deny list", "system partition write", "root", "flash"]\n'
    printf '}\n'
} > "$1/metadata.json"

write_restore() {
    local dir="$1"
    local package_name="$2"
    cat > "$dir/restore.sh" <<EOF
#!/usr/bin/env bash
set -u
EOF
    if [ -n "$package_name" ]; then
        cat >> "$dir/restore.sh" <<EOF
adb -s '$SERIAL' shell cmd package clear-package-preferred-activities '$package_name'
EOF
    fi
    cat >> "$dir/restore.sh" <<EOF
adb -s '$SERIAL' shell cmd package set-home-activity '$FIRE_COMPONENT'
EOF
    if [ -n "$package_name" ]; then
        cat >> "$dir/restore.sh" <<EOF
adb -s '$SERIAL' uninstall '$package_name'
EOF
    fi
    chmod +x "$dir/restore.sh"
}

finish_hashes() {
    local dir="$1"
    write_sha256_manifest "$dir" "$dir/sha256sums.txt"
}

prepare_dir() {
    local dir="$1"
    local test_id="$2"
    local package_name="$3"
    local priority="$4"
    [ ! -e "$dir" ] || fail "refusing to overwrite evidence directory: $dir"
    mkdir -p "$dir/before" "$dir/after"
    : > "$dir/commands.txt"
    printf 'label\tstatus\tstarted_utc\tfinished_utc\tcommand\tstdout\n' > "$dir/command-manifest.tsv"
    write_metadata "$dir" "$test_id" "$package_name" "$priority"
    write_restore "$dir" "$package_name"
}

if [ "$REUSE_PRE_SNAPSHOT" -eq 0 ]; then
    capture_cmd "$PRE_DIR" pre_devices no devices -l
    capture_state "$PRE_DIR/before" baseline com.amazon.firelauncher
    write_metadata "$PRE_DIR" HOME-PRIORITY-PRE '' -1
    write_restore "$PRE_DIR" ''
fi

wait_for_device() {
    local dir="$1"
    local elapsed=0
    : > "$dir/reconnect_poll.tsv"
    printf 'elapsed_seconds\tstate\tpackage_probe\tutc\n' >> "$dir/reconnect_poll.tsv"
    while [ "$elapsed" -lt "$WAIT_SECONDS" ]; do
        local state package_probe
        state=$(adb -s "$SERIAL" get-state 2>&1 || true)
        if [ "$state" = device ]; then
            package_probe=$(adb -s "$SERIAL" shell cmd package resolve-activity --brief \
                -a android.intent.action.MAIN -c android.intent.category.HOME --user 0 2>&1 || true)
            package_probe=${package_probe//$'\n'/ }
            printf '%s\t%s\t%s\t%s\n' "$elapsed" "$state" "$package_probe" "$(timestamp_utc)" \
                >> "$dir/reconnect_poll.tsv"
            case "$package_probe" in
                *"Can't find service"*|*"Can't find package"*|"") ;;
                *) return 0 ;;
            esac
        else
            printf '%s\t%s\t%s\t%s\n' "$elapsed" "$state" '' "$(timestamp_utc)" \
                >> "$dir/reconnect_poll.tsv"
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done
    return 1
}

home_key_probe() {
    local dir="$1"
    capture_cmd "$dir" logcat_clear yes logcat -c
    adb -s "$SERIAL" logcat -b all -v threadtime > "$dir/logcat.txt" 2>&1 &
    local log_pid=$!
    sleep 1
    capture_cmd "$dir" keyevent_home yes shell input keyevent 3
    HOME_KEY_STATUS="$LAST_STATUS"
    sleep 5
    kill "$log_pid" 2>/dev/null || true
    wait "$log_pid" 2>/dev/null || true
    capture_state "$dir/after" after_keyevent
}

for index in "${!PACKAGES[@]}"; do
    package_name="${PACKAGES[$index]}"
    priority="${PRIORITIES[$index]}"
    test_id="HOME-PRIORITY-P${priority}"
    apk="$APK_DIR/$package_name.apk"
    test_dir="$OUTPUT_ROOT/$test_id"
    [ -f "$apk" ] || fail "APK not found: $apk"
    prepare_dir "$test_dir" "$test_id" "$package_name" "$priority"

    capture_state "$test_dir/before" baseline "$package_name"
    host_cmd "$test_dir" install yes install "$apk"
    install_status="$LAST_STATUS"
    capture_cmd "$test_dir" package_path yes shell pm path "$package_name"
    capture_cmd "$test_dir" package_dump no shell dumpsys package "$package_name"
    capture_cmd "$test_dir" candidate_after_install no shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
    capture_cmd "$test_dir" resolve_after_install no shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
    initial_resolve="$LAST_STATUS"
    capture_state "$test_dir/after" after_install "$package_name"

    host_cmd "$test_dir" explicit_start yes shell am start -n "$package_name/org.fireosresearch.home.HomeActivity"
    capture_cmd "$test_dir" explicit_home_intent yes shell am start -a android.intent.action.MAIN -c android.intent.category.HOME
    capture_cmd "$test_dir" prepare_settings yes shell am start -a android.settings.SETTINGS
    sleep 2
    home_key_probe "$test_dir"
    keyevent_status="$HOME_KEY_STATUS"

    capture_cmd "$test_dir" set_home yes shell cmd package set-home-activity "$package_name/org.fireosresearch.home.HomeActivity"
    set_home_status="$LAST_STATUS"
    capture_state "$test_dir/after" after_set_home "$package_name"
    capture_cmd "$test_dir" preferred_home_intent yes shell am start -a android.intent.action.MAIN -c android.intent.category.HOME
    capture_cmd "$test_dir" prepare_settings_preferred yes shell am start -a android.settings.SETTINGS
    sleep 2
    home_key_probe "$test_dir"
    preferred_key_status="$HOME_KEY_STATUS"

    capture_cmd "$test_dir" sleep_screen yes shell input keyevent 223
    sleep_status="$LAST_STATUS"
    sleep 2
    capture_cmd "$test_dir" wake_screen yes shell input keyevent 224
    wake_status="$LAST_STATUS"
    sleep 2
    capture_state "$test_dir/after" after_lock_wake "$package_name"
    lock_wake_status="$wake_status"

    capture_cmd "$test_dir" reboot yes reboot
    reboot_status="$LAST_STATUS"
    if [ "$reboot_status" -eq 0 ] && wait_for_device "$test_dir"; then
        capture_cmd "$test_dir" reboot_home_resolve yes shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
        reboot_resolve_status="$LAST_STATUS"
        capture_state "$test_dir/after" after_reboot "$package_name"
        capture_cmd "$test_dir" post_reboot_home_key yes shell input keyevent 3
        sleep 5
        capture_state "$test_dir/after" after_reboot_home_key "$package_name"
    else
        printf 'ADB did not return within %s seconds after reboot; stopping before restore.\n' "$WAIT_SECONDS" > "$test_dir/reboot_failure.txt"
        finish_hashes "$test_dir"
        finish_hashes "$PRE_DIR"
        fail "ADB did not return after $test_id reboot; inspect $test_dir"
    fi

    capture_cmd "$test_dir" clear_preferred yes shell cmd package clear-package-preferred-activities "$package_name"
    clear_status="$LAST_STATUS"
    capture_cmd "$test_dir" restore_fire yes shell cmd package set-home-activity "$FIRE_COMPONENT"
    restore_status="$LAST_STATUS"
    host_cmd "$test_dir" uninstall yes uninstall "$package_name"
    uninstall_status="$LAST_STATUS"
    capture_state "$test_dir/after" final com.amazon.firelauncher
    capture_cmd "$test_dir/after" final_home_resolve yes shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
    final_resolve_status="$LAST_STATUS"

    final_resolve_text=$(cat "$test_dir/after/final_home_resolve.stdout.txt" "$test_dir/after/final_home_resolve.stderr.txt" 2>/dev/null || true)
    final_status=FAIL
    if printf '%s\n' "$final_resolve_text" | grep -q 'com.amazon.firelauncher/.Launcher' \
        && [ "$uninstall_status" -eq 0 ] && [ "$restore_status" -eq 0 ]; then
        final_status=RESTORED_FIRE
    fi
    confidence=Hypothesis
    if [ "$final_status" = RESTORED_FIRE ]; then
        confidence=Strong_evidence
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$test_id" "$package_name" "$priority" "$install_status" "$initial_resolve" \
        "$set_home_status" "$preferred_key_status" "$keyevent_status" "$lock_wake_status" \
        "$reboot_status" "$reboot_resolve_status" "$clear_status" "$restore_status" \
        "$uninstall_status" "$final_resolve_status" "$final_status" "$confidence" >> "$MATRIX"

    {
        printf '# %s\n\n' "$test_id"
        printf -- '- Package: `%s`\n' "$package_name"
        printf -- '- Declared priority: `%s`\n' "$priority"
        printf -- '- Install exit status: `%s`\n' "$install_status"
        printf -- '- `set-home-activity` exit status: `%s`\n' "$set_home_status"
        printf -- '- Reboot exit status: `%s`\n' "$reboot_status"
        printf -- '- Restore Fire exit status: `%s`\n' "$restore_status"
        printf -- '- Uninstall exit status: `%s`\n' "$uninstall_status"
        printf -- '- Final state: `%s`\n' "$final_status"
        printf -- '- Interpretation: `Hypothesis` until the raw candidate, resolver, preferred, activity, window, and logcat outputs are reviewed.\n'
    } > "$test_dir/result.md"
    finish_hashes "$test_dir"
done

finish_hashes "$PRE_DIR"
printf 'Phase 3A priority experiment completed; inspect %s and per-test result.md files.\n' "$MATRIX"
