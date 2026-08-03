#!/usr/bin/env bash
# Reproducible, offline-only APK inspection. This script never contacts a device.
set -u

APK=""
OUTPUT=""
DRY_RUN=0

usage() {
    cat <<'EOF'
Usage:
  inspect_apk_static.sh --apk FILE --output DIR [--dry-run]

The script performs offline inspection only and refuses to reuse an output
directory. It does not install, launch, or modify the APK.
EOF
}

fail() {
    echo "ERROR: $*" >&2
    exit 2
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --apk)
            [ "$#" -ge 2 ] || fail "--apk requires a value"
            APK="$2"
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

[ -n "$APK" ] || fail "an APK path is required"
[ -n "$OUTPUT" ] || fail "an output directory is required"
[ -f "$APK" ] || fail "APK does not exist: $APK"
case "$OUTPUT" in
    /|.|..|"" ) fail "refusing unsafe output directory: $OUTPUT" ;;
esac

JAVA_HOME="${JAVA_HOME:-/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home}"
export JAVA_HOME
PATH="${JAVA_HOME}/bin:${PATH}"
export PATH

commands=(
    "file $APK"
    "shasum -a 256 $APK"
    "unzip -t $APK"
    "apkanalyzer manifest permissions $APK"
    "apkanalyzer manifest print $APK"
    "apkanalyzer apk summary $APK"
    "apkanalyzer apk file-size $APK"
    "apkanalyzer manifest application-id $APK"
    "apkanalyzer manifest version-code $APK"
    "apkanalyzer manifest version-name $APK"
    "apkanalyzer manifest min-sdk $APK"
    "apkanalyzer manifest target-sdk $APK"
    "unzip -l $APK"
)

if [ "$DRY_RUN" -eq 1 ]; then
    printf '%s\n' "DRY-RUN: no APK will be modified; planned offline commands:"
    printf '  %s\n' "${commands[@]}"
    printf '%s\n' "DRY-RUN: output would be written to $OUTPUT"
    exit 0
fi

[ ! -e "$OUTPUT" ] || fail "output directory already exists; refusing to overwrite: $OUTPUT"
mkdir -p "$OUTPUT"

printf 'apk=%s\ninspection_timestamp_utc=%s\njava_home=%s\n' \
    "$APK" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$JAVA_HOME" > "$OUTPUT/metadata.txt"
printf '%s\n' "${commands[@]}" > "$OUTPUT/commands.txt"

run_capture() {
    local label="$1"
    shift
    "$@" > "$OUTPUT/$label.stdout.txt" 2> "$OUTPUT/$label.stderr.txt"
    printf '%s\n' "$?" > "$OUTPUT/$label.exit_code.txt"
}

run_capture file file "$APK"
run_capture sha256 shasum -a 256 "$APK"
run_capture zip_test unzip -t "$APK"
run_capture manifest_permissions apkanalyzer manifest permissions "$APK"
run_capture manifest_print apkanalyzer manifest print "$APK"
run_capture apk_summary apkanalyzer apk summary "$APK"
run_capture apk_file_size apkanalyzer apk file-size "$APK"
run_capture application_id apkanalyzer manifest application-id "$APK"
run_capture version_code apkanalyzer manifest version-code "$APK"
run_capture version_name apkanalyzer manifest version-name "$APK"
run_capture min_sdk apkanalyzer manifest min-sdk "$APK"
run_capture target_sdk apkanalyzer manifest target-sdk "$APK"
run_capture zip_listing unzip -l "$APK"

unzip -p "$APK" classes.dex > "$OUTPUT/classes.dex"
printf '%s\n' "$?" > "$OUTPUT/classes.dex.exit_code.txt"
strings "$OUTPUT/classes.dex" | rg -i 'juniojsv|BootReceiver|ExploitHandler|MainActivity|mtk-su|magisk|root|reboot|exec' \
    > "$OUTPUT/classes-selected-strings.txt" 2> "$OUTPUT/classes-selected-strings.stderr.txt"
printf '%s\n' "$?" > "$OUTPUT/classes-selected-strings.exit_code.txt"

unzip -l "$APK" | rg -i 'AndroidManifest|classes[0-9]*\\.dex|magisk|mtk-su|META-INF|lib/' \
    > "$OUTPUT/key-entries.txt" 2> "$OUTPUT/key-entries.stderr.txt"
printf '%s\n' "$?" > "$OUTPUT/key-entries.exit_code.txt"

find "$OUTPUT" -type f -not -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
{
    printf '%s\n\n' '# Offline APK inspection'
    printf -- '- APK: `%s`\n' "$APK"
    printf '%s\n' '- No device command was executed.'
    printf '%s\n' '- No APK content was modified.'
    printf '%s\n' '- Raw command output and exit codes are preserved in this directory.'
    printf '%s\n' '- SHA-256: `sha256sums.txt`'
} > "$OUTPUT/result.md"

echo "Offline APK inspection written to $OUTPUT"
