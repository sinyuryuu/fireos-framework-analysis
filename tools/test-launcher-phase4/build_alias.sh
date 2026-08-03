#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
MANIFEST="$SCRIPT_DIR/config/AndroidManifest.xml"
SOURCE_DIR="$SCRIPT_DIR/src"
OUTPUT=""
SDK_ROOT="${ANDROID_SDK_ROOT:-/opt/homebrew/share/android-commandlinetools}"
PLATFORM_API=35
BUILD_TOOLS_VERSION=35.0.0
KEYSTORE=""
KEYSTORE_PASSWORD=""
KEY_ALIAS=fireos-phase4
DRY_RUN=0

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }
sha256_file() { shasum -a 256 "$1" | awk '{print $1}'; }
usage() {
  cat <<'EOF'
Usage: build_alias.sh --output DIR --keystore FILE --keystore-password PASSWORD
                      [--sdk-root DIR] [--dry-run]
EOF
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
[ -f "$MANIFEST" ] || fail "manifest not found: $MANIFEST"
[ -d "$SOURCE_DIR" ] || fail "source directory not found: $SOURCE_DIR"
AAPT2="$SDK_ROOT/build-tools/$BUILD_TOOLS_VERSION/aapt2"
D8="$SDK_ROOT/build-tools/$BUILD_TOOLS_VERSION/d8"
ZIPALIGN="$SDK_ROOT/build-tools/$BUILD_TOOLS_VERSION/zipalign"
APKSIGNER="$SDK_ROOT/build-tools/$BUILD_TOOLS_VERSION/apksigner"
ANDROID_JAR="$SDK_ROOT/platforms/android-$PLATFORM_API/android.jar"

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no APK or build output created.\n'
  printf 'DRY-RUN: output=%s sdk=%s platform=%s build-tools=%s\n' "$OUTPUT" "$SDK_ROOT" "$PLATFORM_API" "$BUILD_TOOLS_VERSION"
  printf 'DRY-RUN: AGP=NOT_USED Gradle=NOT_USED; manifest=%s; source=%s\n' "$MANIFEST" "$SOURCE_DIR"
  printf 'DRY-RUN: required tools: javac jar keytool aapt2 d8 zipalign apksigner\n'
  exit 0
fi

case "$OUTPUT" in /|.|..|"") fail 'unsafe output directory' ;; esac
[ ! -e "$OUTPUT" ] || fail "refusing to overwrite existing output: $OUTPUT"
[ -n "$KEYSTORE" ] || fail '--keystore is required'
[ -n "$KEYSTORE_PASSWORD" ] || fail '--keystore-password is required'
[ -f "$KEYSTORE" ] || fail "keystore not found: $KEYSTORE"
[ -d "$(dirname -- "$OUTPUT")" ] || mkdir -p "$(dirname -- "$OUTPUT")"
OUTPUT="$(CDPATH= cd -- "$(dirname -- "$OUTPUT")" && pwd)/$(basename -- "$OUTPUT")"
for command_name in java javac jar keytool; do command -v "$command_name" >/dev/null || fail "missing $command_name"; done
for path in "$AAPT2" "$D8" "$ZIPALIGN" "$APKSIGNER" "$ANDROID_JAR"; do [ -f "$path" ] || fail "missing SDK file $path"; done

mkdir -p "$OUTPUT/work/java" "$OUTPUT/work/classes" "$OUTPUT/work/dex" "$OUTPUT/work/res/values"
cp "$MANIFEST" "$OUTPUT/manifest.xml"
cp -R "$SOURCE_DIR" "$OUTPUT/source"
printf 'field\tvalue\n' > "$OUTPUT/build-manifest.tsv"
printf 'build_started_utc\t%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$OUTPUT/build-manifest.tsv"
printf 'project_relative\ttools/test-launcher-phase4\nandroid_gradle_plugin\tNOT_USED\ngradle\tNOT_USED\n' >> "$OUTPUT/build-manifest.tsv"
printf 'sdk_root\t%s\nplatform_api\t%s\nbuild_tools\t%s\n' "$SDK_ROOT" "$PLATFORM_API" "$BUILD_TOOLS_VERSION" >> "$OUTPUT/build-manifest.tsv"
printf 'manifest_sha256\t%s\n' "$(sha256_file "$MANIFEST")" >> "$OUTPUT/build-manifest.tsv"
find "$SOURCE_DIR" -type f -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/source-sha256sums.txt"
java -version 2> "$OUTPUT/java-version.txt" || true
javac -version > "$OUTPUT/javac-version.txt" 2>&1 || true
"$AAPT2" version > "$OUTPUT/aapt2-version.txt" 2>&1
"$D8" --version > "$OUTPUT/d8-version.txt" 2>&1
"$APKSIGNER" --version > "$OUTPUT/apksigner-version.txt" 2>&1
"$AAPT2" compile --dir "$OUTPUT/work/res" -o "$OUTPUT/work/resources.zip"
"$AAPT2" link -o "$OUTPUT/work/unsigned.apk" -I "$ANDROID_JAR" --manifest "$MANIFEST" \
  --min-sdk-version 28 --target-sdk-version 28 --version-code 1 --version-name 1.0 \
  --java "$OUTPUT/work/java" "$OUTPUT/work/resources.zip"
javac -source 8 -target 8 -classpath "$ANDROID_JAR" -d "$OUTPUT/work/classes" \
  $(find "$SOURCE_DIR" -name '*.java' -print)
jar --create --file "$OUTPUT/work/classes.jar" -C "$OUTPUT/work/classes" .
"$D8" --lib "$ANDROID_JAR" --min-api 28 --output "$OUTPUT/work/dex" "$OUTPUT/work/classes.jar"
APK_UNSIGNED="$OUTPUT/work/unsigned.apk"
touch -t 198001010000 "$OUTPUT/work/dex/classes.dex" "$APK_UNSIGNED"
(cd "$OUTPUT/work/dex" && zip -X -q "$APK_UNSIGNED" classes.dex)
"$ZIPALIGN" -f 4 "$APK_UNSIGNED" "$OUTPUT/work/aligned.apk"
"$APKSIGNER" sign --ks "$KEYSTORE" --ks-key-alias "$KEY_ALIAS" --ks-pass "pass:$KEYSTORE_PASSWORD" \
  --v4-signing-enabled false --out "$OUTPUT/org.fireosresearch.phase4.alias.apk" "$OUTPUT/work/aligned.apk"
"$APKSIGNER" verify --verbose "$OUTPUT/org.fireosresearch.phase4.alias.apk" > "$OUTPUT/apksigner-verify.txt"
printf 'apk_sha256\t%s\n' "$(sha256_file "$OUTPUT/org.fireosresearch.phase4.alias.apk")" >> "$OUTPUT/build-manifest.tsv"
tar -cf - -C "$SCRIPT_DIR" README.md config src | gzip -n > "$OUTPUT/phase4-alias-source.tar.gz"
printf 'source_archive_sha256\t%s\n' "$(sha256_file "$OUTPUT/phase4-alias-source.tar.gz")" >> "$OUTPUT/build-manifest.tsv"
printf 'build_finished_utc\t%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$OUTPUT/build-manifest.tsv"
find "$OUTPUT" -type f ! -path "$OUTPUT/work/*" -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Phase 4 alias APK built in %s\n' "$OUTPUT"
