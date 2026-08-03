#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
VARIANTS_FILE="$SCRIPT_DIR/config/variants.tsv"
SOURCE_FILE="$SCRIPT_DIR/src/org/fireosresearch/home/HomeActivity.java"

OUTPUT=""
SDK_ROOT="${ANDROID_SDK_ROOT:-/opt/homebrew/share/android-commandlinetools}"
PLATFORM_API="35"
BUILD_TOOLS_VERSION="35.0.0"
KEYSTORE=""
KEYSTORE_PASSWORD=""
KEY_ALIAS="fireos-phase3a"
DRY_RUN=0

usage() {
    cat <<'EOF'
Usage:
  build_variants.sh --output DIR --keystore FILE --keystore-password PASSWORD
                     [--sdk-root DIR] [--platform-api API]
                     [--build-tools VERSION] [--key-alias ALIAS]
                     [--dry-run]

Builds five small HOME APK variants with raw Android SDK tools. Android Gradle
Plugin and Gradle are not used. The output directory must not already exist.
EOF
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 2
}

sha256_file() {
    if command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$1" | awk '{print $1}'
    else
        sha256sum "$1" | awk '{print $1}'
    fi
}

timestamp_utc() {
    date -u '+%Y-%m-%dT%H:%M:%SZ'
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --output) [ "$#" -ge 2 ] || fail '--output requires a value'; OUTPUT="$2"; shift 2 ;;
        --sdk-root) [ "$#" -ge 2 ] || fail '--sdk-root requires a value'; SDK_ROOT="$2"; shift 2 ;;
        --platform-api) [ "$#" -ge 2 ] || fail '--platform-api requires a value'; PLATFORM_API="$2"; shift 2 ;;
        --build-tools) [ "$#" -ge 2 ] || fail '--build-tools requires a value'; BUILD_TOOLS_VERSION="$2"; shift 2 ;;
        --keystore) [ "$#" -ge 2 ] || fail '--keystore requires a value'; KEYSTORE="$2"; shift 2 ;;
        --keystore-password) [ "$#" -ge 2 ] || fail '--keystore-password requires a value'; KEYSTORE_PASSWORD="$2"; shift 2 ;;
        --key-alias) [ "$#" -ge 2 ] || fail '--key-alias requires a value'; KEY_ALIAS="$2"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) fail "unknown argument: $1" ;;
    esac
done

[ -n "$OUTPUT" ] || fail '--output is required'
[ -f "$VARIANTS_FILE" ] || fail "variants file not found: $VARIANTS_FILE"
[ -f "$SOURCE_FILE" ] || fail "source file not found: $SOURCE_FILE"

AAPT2="$SDK_ROOT/build-tools/$BUILD_TOOLS_VERSION/aapt2"
D8="$SDK_ROOT/build-tools/$BUILD_TOOLS_VERSION/d8"
ZIPALIGN="$SDK_ROOT/build-tools/$BUILD_TOOLS_VERSION/zipalign"
APKSIGNER="$SDK_ROOT/build-tools/$BUILD_TOOLS_VERSION/apksigner"
ANDROID_JAR="$SDK_ROOT/platforms/android-$PLATFORM_API/android.jar"

planned_commands=(
    "java -version"
    "javac -version"
    "jar --version"
    "keytool -help"
    "$AAPT2 version"
    "$D8 --version"
    "$ZIPALIGN -h"
    "$APKSIGNER --version"
)

if [ "$DRY_RUN" -eq 1 ]; then
    printf 'DRY-RUN: no APK or filesystem build output will be created.\n'
    printf 'DRY-RUN: output=%s sdk-root=%s platform=android-%s build-tools=%s\n' \
        "$OUTPUT" "$SDK_ROOT" "$PLATFORM_API" "$BUILD_TOOLS_VERSION"
    printf 'DRY-RUN: AGP=NOT_USED Gradle=NOT_USED\n'
    printf 'DRY-RUN: required tool probes:\n'
    printf '  %s\n' "${planned_commands[@]}"
    printf 'DRY-RUN: variants:\n'
    awk 'BEGIN { FS="[[:space:]]+" } /^[[:space:]]*#/ || NF == 0 { next } { print "  package=" $1 " priority=" $2 }' "$VARIANTS_FILE"
    exit 0
fi

case "$OUTPUT" in
    /|.|..|"") fail "refusing unsafe output directory: $OUTPUT" ;;
esac
[ ! -e "$OUTPUT" ] || fail "refusing to overwrite existing output directory: $OUTPUT"
[ -d "$(dirname -- "$OUTPUT")" ] || fail "output parent directory does not exist: $(dirname -- "$OUTPUT")"
OUTPUT="$(CDPATH= cd -- "$(dirname -- "$OUTPUT")" && pwd)/$(basename -- "$OUTPUT")"
[ -n "$KEYSTORE" ] || fail '--keystore is required for a non-dry build'
[ -n "$KEYSTORE_PASSWORD" ] || fail '--keystore-password is required for a non-dry build'
[ -f "$KEYSTORE" ] || fail "keystore not found: $KEYSTORE"

for command_name in java javac jar keytool; do
    command -v "$command_name" >/dev/null 2>&1 || fail "required JDK command not found: $command_name"
done
for tool_path in "$AAPT2" "$D8" "$ZIPALIGN" "$APKSIGNER" "$ANDROID_JAR"; do
    [ -f "$tool_path" ] || fail "required SDK file not found: $tool_path"
done

mkdir -p "$OUTPUT"
BUILD_STARTED=$(timestamp_utc)
SOURCE_SHA256=$(sha256_file "$SOURCE_FILE")
VARIANTS_SHA256=$(sha256_file "$VARIANTS_FILE")

printf 'field\tvalue\n' > "$OUTPUT/build-manifest.tsv"
printf 'build_started_utc\t%s\n' "$BUILD_STARTED" >> "$OUTPUT/build-manifest.tsv"
printf 'project_relative\ttools/test-launcher\n' >> "$OUTPUT/build-manifest.tsv"
printf 'android_gradle_plugin\tNOT_USED\n' >> "$OUTPUT/build-manifest.tsv"
printf 'gradle\tNOT_USED\n' >> "$OUTPUT/build-manifest.tsv"
printf 'sdk_root\t%s\n' "$SDK_ROOT" >> "$OUTPUT/build-manifest.tsv"
printf 'platform_api\t%s\n' "$PLATFORM_API" >> "$OUTPUT/build-manifest.tsv"
printf 'build_tools\t%s\n' "$BUILD_TOOLS_VERSION" >> "$OUTPUT/build-manifest.tsv"
printf 'source_sha256\t%s\n' "$SOURCE_SHA256" >> "$OUTPUT/build-manifest.tsv"
printf 'variants_sha256\t%s\n' "$VARIANTS_SHA256" >> "$OUTPUT/build-manifest.tsv"
java -version 2> "$OUTPUT/java-version.txt" || fail 'java is not runnable'
javac -version 2> "$OUTPUT/javac-version.txt" || fail 'javac is not runnable'
keytool -help > "$OUTPUT/keytool-help.txt" 2>&1 || true
"$AAPT2" version > "$OUTPUT/aapt2-version.txt" 2>&1 || fail 'aapt2 probe failed'
"$D8" --version > "$OUTPUT/d8-version.txt" 2>&1 || fail 'd8 probe failed'
"$ZIPALIGN" -h > "$OUTPUT/zipalign-version.txt" 2>&1 || true
"$APKSIGNER" --version > "$OUTPUT/apksigner-version.txt" 2>&1 || fail 'apksigner probe failed'

if ! keytool -list -keystore "$KEYSTORE" -storepass "$KEYSTORE_PASSWORD" -alias "$KEY_ALIAS" \
    > "$OUTPUT/keystore-list.txt" 2>&1; then
    fail "keystore alias not found or password rejected: $KEY_ALIAS"
fi

build_one() {
    local package_name="$1"
    local priority="$2"
    local safe_name="${package_name##*.}"
    local work="$OUTPUT/work/$safe_name"
    local apk="$OUTPUT/$package_name.apk"
    local manifest="$work/AndroidManifest.xml"
    local java_out="$work/java"
    local classes="$work/classes"
    local classes_jar="$work/classes.jar"
    local dex="$work/dex"
    local res="$work/res"
    local compiled_res="$work/resources.zip"
    local unsigned="$work/unsigned.apk"
    local unsigned_abs="$unsigned"
    local aligned="$work/aligned.apk"

    mkdir -p "$work" "$java_out" "$classes" "$dex" "$res/values"
    cp "$SOURCE_FILE" "$work/HomeActivity.java"
    cat > "$manifest" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="$package_name">
    <application
        android:label="Phase 3A $package_name priority $priority"
        android:theme="@android:style/Theme.Material.Light.NoActionBar"
        android:allowBackup="false"
        android:supportsRtl="true">
        <meta-data
            android:name="org.fireosresearch.home.PRIORITY"
            android:value="$priority" />
        <activity
            android:name="org.fireosresearch.home.HomeActivity"
            android:exported="true"
            android:launchMode="singleTask">
            <intent-filter android:priority="$priority">
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.HOME" />
                <category android:name="android.intent.category.DEFAULT" />
            </intent-filter>
        </activity>
    </application>
</manifest>
EOF
    cat > "$res/values/strings.xml" <<EOF
<resources><string name="app_name">Phase 3A $package_name p$priority</string></resources>
EOF

    "$AAPT2" compile --dir "$res" -o "$compiled_res"
    "$AAPT2" link -o "$unsigned" -I "$ANDROID_JAR" --manifest "$manifest" \
        --min-sdk-version 28 --target-sdk-version 28 --version-code 1 \
        --version-name 1.0 --java "$java_out" "$compiled_res"
    javac -source 8 -target 8 -classpath "$ANDROID_JAR" -d "$classes" "$work/HomeActivity.java"
    jar --create --file "$classes_jar" -C "$classes" .
    "$D8" --lib "$ANDROID_JAR" --min-api 28 --output "$dex" "$classes_jar"
    TZ=UTC touch -t 198001010000 "$dex/classes.dex" "$unsigned"
    (cd "$dex" && zip -X -q "$unsigned_abs" classes.dex)
    "$ZIPALIGN" -f 4 "$unsigned" "$aligned"
    "$APKSIGNER" sign --ks "$KEYSTORE" --ks-key-alias "$KEY_ALIAS" \
        --ks-pass "pass:$KEYSTORE_PASSWORD" --v4-signing-enabled false \
        --out "$apk" "$aligned"
    "$APKSIGNER" verify --verbose "$apk" > "$work/apksigner-verify.txt"
    sha256_file "$apk" > "$OUTPUT/$package_name.sha256"
    printf 'variant_package\t%s\npriority\t%s\napk\t%s\napk_sha256\t%s\n' \
        "$package_name" "$priority" "$apk" "$(cat "$OUTPUT/$package_name.sha256")" \
        >> "$OUTPUT/build-manifest.tsv"
}

while IFS=$'\t' read -r package_name priority; do
    case "$package_name" in
        ''|\#*) continue ;;
    esac
    [ -n "$priority" ] || fail "missing priority for $package_name"
    build_one "$package_name" "$priority"
done < "$VARIANTS_FILE"

tar -cf - -C "$SCRIPT_DIR" README.md config src | gzip -n > "$OUTPUT/phase3a-launcher-source.tar.gz"
printf 'source_archive_sha256\t%s\n' "$(sha256_file "$OUTPUT/phase3a-launcher-source.tar.gz")" >> "$OUTPUT/build-manifest.tsv"
printf 'build_finished_utc\t%s\n' "$(timestamp_utc)" >> "$OUTPUT/build-manifest.tsv"

find "$OUTPUT" -type f ! -name sha256sums.txt ! -path "$OUTPUT/work/*" -print0 | while IFS= read -r -d '' file; do
    printf '%s  %s\n' "$(sha256_file "$file")" "${file#"$OUTPUT"/}"
done | sort > "$OUTPUT/sha256sums.txt"
printf 'Launcher variants built in %s\n' "$OUTPUT"
