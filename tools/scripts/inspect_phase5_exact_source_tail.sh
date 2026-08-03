#!/usr/bin/env bash
# Sample a bounded tail range of an official bzip2 source archive.
# Host-side evidence collection only; never invokes adb, fastboot, or a device command.
set -Eeuo pipefail

SOURCE_URL=""
OUTPUT=""
RANGE_START=""
RANGE_END=""
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --url) [ "$#" -ge 2 ] || die '--url requires a value'; SOURCE_URL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --range-start) [ "$#" -ge 2 ] || die '--range-start requires a value'; RANGE_START="$2"; shift 2 ;;
    --range-end) [ "$#" -ge 2 ] || die '--range-end requires a value'; RANGE_END="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: inspect_phase5_exact_source_tail.sh --url URL --output DIR --range-start BYTES --range-end BYTES [--dry-run]'
      exit 0
      ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SOURCE_URL" ] || die '--url is required'
[ -n "$OUTPUT" ] || die '--output is required'
[[ "$RANGE_START" =~ ^[0-9]+$ ]] || die '--range-start must be numeric'
[[ "$RANGE_END" =~ ^[0-9]+$ ]] || die '--range-end must be numeric'
[ "$RANGE_START" -lt "$RANGE_END" ] || die '--range-start must be smaller than --range-end'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no network request will execute.\n'
  printf 'DRY-RUN: curl --range %s-%s --max-time 300 %q -o %q\n' \
    "$RANGE_START" "$RANGE_END" "$SOURCE_URL" "$OUTPUT/source-tail.range"
  printf '%s\n' 'DRY-RUN: bzip2recover source-tail.range'
  printf '%s\n' 'DRY-RUN: strings -n 4 recovered-block | filter MT8183 and boot-chain markers'
  exit 0
fi

case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac
[ ! -e "$OUTPUT" ] || die "output directory already exists: $OUTPUT"
mkdir -p "$OUTPUT"
OUTPUT="$(cd "$OUTPUT" && pwd)"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/phase5-source-tail.XXXXXX")"
cleanup() { rm -rf "$WORK_DIR"; }
trap cleanup EXIT

printf 'source_url=%s\nrange=bytes=%s-%s\nsampling_timestamp_utc=%s\n' \
  "$SOURCE_URL" "$RANGE_START" "$RANGE_END" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.tsv"
printf '%s\n' \
  "curl --fail --retry 2 --max-time 300 --range $RANGE_START-$RANGE_END $SOURCE_URL -o $OUTPUT/source-tail.range" \
  'bzip2recover source-tail.range' \
  'strings -n 4 recovered-block | filter MT8183 and boot-chain markers' \
  > "$OUTPUT/commands.txt"

curl --fail --retry 2 --max-time 300 -sS --range "$RANGE_START-$RANGE_END" \
  "$SOURCE_URL" -o "$OUTPUT/source-tail.range" 2> "$OUTPUT/curl.stderr.txt"
printf '%s\n' "$?" > "$OUTPUT/curl.exit_code.txt"
shasum -a 256 "$OUTPUT/source-tail.range" > "$OUTPUT/source-tail.range.sha256"
wc -c "$OUTPUT/source-tail.range" > "$OUTPUT/source-tail.range.size.txt"

cp "$OUTPUT/source-tail.range" "$WORK_DIR/source-tail.range"
(
  cd "$WORK_DIR"
  bzip2recover source-tail.range > "$OUTPUT/bzip2recover.stdout.txt" 2> "$OUTPUT/bzip2recover.stderr.txt"
)
printf '%s\n' "$?" > "$OUTPUT/bzip2recover.exit_code.txt"
find "$WORK_DIR" -maxdepth 1 -type f -name 'rec*' -print | sort > "$OUTPUT/recovered-blocks.list.txt"
printf 'recovered_blocks=%s\n' "$(wc -l < "$OUTPUT/recovered-blocks.list.txt" | tr -d ' ')" > "$OUTPUT/recovered-blocks.count.txt"

MT8183_MATCHES="$OUTPUT/mt8183-source-paths.txt"
BOOTCHAIN_MATCHES="$OUTPUT/boot-chain-source-matches.txt"
: > "$MT8183_MATCHES"
: > "$BOOTCHAIN_MATCHES"
for recovered in "$WORK_DIR"/rec*; do
  [ -f "$recovered" ] || continue
  strings -n 4 "$recovered" 2>/dev/null || true
done | sort -u > "$WORK_DIR/strings.sorted.txt"

rg -i '^kernel/mediatek/mt8183/' "$WORK_DIR/strings.sorted.txt" \
  | sed 's/[[:cntrl:]]//g' \
  | sort -u > "$MT8183_MATCHES" || true
rg -i '(^|/)(preloader|lk|u-boot|uboot|bootrom|bootloader)(/|\\.|$)|PS7330|MTK_BLOADER|daa_enabled|download agent' \
  "$WORK_DIR/strings.sorted.txt" \
  | sed 's/[[:cntrl:]]//g' \
  | sort -u > "$BOOTCHAIN_MATCHES" || true

cat > "$OUTPUT/result.md" <<EOF
# Exact-version source tail sample

- URL: $SOURCE_URL
- Range: bytes $RANGE_START-$RANGE_END
- The range is a damaged/truncated bzip2 stream by design; bzip2recover
  recovered independent blocks for offline string/path inspection.
- This sample is not a complete tar listing and must not be treated as a
  complete source archive or a firmware image.
- MT8183 source-path matches are retained in mt8183-source-paths.txt.
- Boot-chain keyword matches are retained in boot-chain-source-matches.txt.
- No device, ADB, fastboot, BROM, DA, loader, or partition operation ran.
EOF

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote source-tail sample summary to %s\n' "$OUTPUT"
