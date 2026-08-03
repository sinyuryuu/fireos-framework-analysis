#!/usr/bin/env bash
# Offline-only inspection. Never installs, launches, or executes an asset.
set -u

APK=""
OUTPUT=""
DRY_RUN=0

usage() {
    cat <<'EOF'
Usage:
  inspect_mtk_easy_su_payload.sh --apk FILE --output DIR [--dry-run]

The APK is inspected offline. The output directory must not already exist.
No extracted binary, shell script, Magisk asset, or APK is executed.
EOF
}

fail() {
    echo "ERROR: $*" >&2
    exit 2
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --apk) [ "$#" -ge 2 ] || fail "--apk requires a value"; APK="$2"; shift 2 ;;
        --output) [ "$#" -ge 2 ] || fail "--output requires a value"; OUTPUT="$2"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) fail "unknown argument: $1" ;;
    esac
done

[ -n "$APK" ] || fail "an APK path is required"
[ -n "$OUTPUT" ] || fail "an output directory is required"
[ -f "$APK" ] || fail "APK does not exist: $APK"
case "$OUTPUT" in /|.|..|"") fail "refusing unsafe output directory: $OUTPUT" ;; esac

ASSETS=(assets/magisk-boot.sh assets/mtk-su32 assets/mtk-su64 assets/magiskinit32 assets/magiskinit64 assets/magisk-manager.apk)
commands=(
    "file $APK"
    "shasum -a 256 $APK"
    "unzip -t $APK"
    "unzip -Z1 $APK"
    "unzip -p $APK assets/magisk-boot.sh | rg -n 'mtk-su|magisk|mount|setenforce|/sbin/su|/proc'"
)

if [ "$DRY_RUN" -eq 1 ]; then
    printf '%s\n' "DRY-RUN: no APK content will be executed; planned offline commands:"
    printf '  %s\n' "${commands[@]}"
    printf '%s\n' "DRY-RUN: output would be written to $OUTPUT"
    exit 0
fi

[ ! -e "$OUTPUT" ] || fail "output directory already exists; refusing to overwrite: $OUTPUT"
mkdir -p "$OUTPUT"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/mtk-easy-su-payload.XXXXXX")" || exit 1
trap 'rm -rf "$TMP_DIR"' EXIT

printf 'apk=%s\ninspection_timestamp_utc=%s\nexecution_policy=offline_only_no_asset_execution\n' \
    "$APK" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.txt"
printf '%s\n' "${commands[@]}" > "$OUTPUT/commands.txt"

run_capture() {
    local label="$1"; shift
    "$@" > "$OUTPUT/$label.stdout.txt" 2> "$OUTPUT/$label.stderr.txt"
    printf '%s\n' "$?" > "$OUTPUT/$label.exit_code.txt"
}

run_capture file file "$APK"
run_capture apk_sha256 shasum -a 256 "$APK"
run_capture zip_test unzip -t "$APK"
run_capture zip_listing unzip -Z1 "$APK"
printf 'asset\tsha256\tbytes\tfile_type\n' > "$OUTPUT/asset-hashes-and-types.tsv"
: > "$OUTPUT/asset-selected-strings.txt"

for asset in "${ASSETS[@]}"; do
    name="${asset#assets/}"
    temp_asset="$TMP_DIR/$name"
    if unzip -p "$APK" "$asset" > "$temp_asset" 2> "$OUTPUT/${name}.extract.stderr.txt"; then
        printf '0\n' > "$OUTPUT/${name}.extract.exit_code.txt"
    else
        printf '%s\n' "$?" > "$OUTPUT/${name}.extract.exit_code.txt"
        printf '%s\n' "$asset" >> "$OUTPUT/missing-assets.txt"
        continue
    fi
    hash="$(shasum -a 256 "$temp_asset" | awk '{print $1}')"
    bytes="$(wc -c < "$temp_asset" | tr -d ' ')"
    type="$(file -b "$temp_asset")"
    printf '%s\t%s\t%s\t%s\n' "$asset" "$hash" "$bytes" "$type" >> "$OUTPUT/asset-hashes-and-types.tsv"
    if command -v strings >/dev/null 2>&1; then
        {
            printf '%s\n' "--- $asset ---"
            strings -a "$temp_asset" | rg -i 'mtk-su|magisk|root|su|mount|setenforce|system_root|trona|mt8183|kftrwi|boot' || true
        } >> "$OUTPUT/asset-selected-strings.txt"
    fi
    if [ "$name" = "magisk-boot.sh" ]; then
        rg -n 'mtk-su|magisk|mount|setenforce|/sbin/su|/proc|/dev/block|pm uninstall|pm install' \
            "$temp_asset" > "$OUTPUT/magisk-boot-command-review.txt" || true
    fi
    case "$name" in
        mtk-su32|mtk-su64|magiskinit32|magiskinit64)
            if command -v readelf >/dev/null 2>&1; then
                readelf -h "$temp_asset" > "$OUTPUT/${name}.readelf-header.txt" 2> "$OUTPUT/${name}.readelf-header.stderr.txt"
                printf '%s\n' "$?" > "$OUTPUT/${name}.readelf-header.exit_code.txt"
            else
                printf '%s\n' 'readelf unavailable' > "$OUTPUT/${name}.readelf-header.txt"
            fi
            ;;
    esac
done

cat > "$OUTPUT/result.md" <<'EOF'
# Offline `mtk-easy-su` payload inspection

- Generated from the APK without installing or launching it.
- No extracted binary, shell script, Magisk asset, or APK was executed.
- `asset-hashes-and-types.tsv` records embedded asset digests and file types.
- `magisk-boot-command-review.txt` is a selected-line review, not an execution trace.
EOF

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
echo "Offline payload inspection written to $OUTPUT"
