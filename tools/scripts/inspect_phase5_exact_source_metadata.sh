#!/usr/bin/env bash
# Bounded metadata inspection for an official Fire source archive.
# Never invokes adb, fastboot, a bootloader tool, or any device-side command.
set -Eeuo pipefail

SOURCE_URL=""
OUTPUT=""
RANGE_END=16777215
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --url) [ "$#" -ge 2 ] || die '--url requires a value'; SOURCE_URL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --range-end) [ "$#" -ge 2 ] || die '--range-end requires a value'; RANGE_END="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: inspect_phase5_exact_source_metadata.sh --url URL --output DIR [--range-end BYTES] [--dry-run]'
      exit 0
      ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SOURCE_URL" ] || die '--url is required'
[ -n "$OUTPUT" ] || die '--output is required'
[[ "$RANGE_END" =~ ^[0-9]+$ ]] || die '--range-end must be numeric'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no network request will execute.\n'
  printf 'DRY-RUN: curl -I --max-time 30 %q\n' "$SOURCE_URL"
  printf 'DRY-RUN: curl --range 0-%s --max-time 120 %q | bzip2 -dc | tar -tvf -\n' "$RANGE_END" "$SOURCE_URL"
  exit 0
fi

case "$OUTPUT" in /|.|..|"") die "unsafe output directory: $OUTPUT" ;; esac
[ ! -e "$OUTPUT" ] || die "output directory already exists: $OUTPUT"
mkdir -p "$OUTPUT"

printf 'source_url=%s\nrange=bytes=0-%s\ninspection_timestamp_utc=%s\n' \
  "$SOURCE_URL" "$RANGE_END" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.tsv"
printf '%s\n' \
  "curl -I --max-time 30 $SOURCE_URL" \
  "curl --range 0-$RANGE_END --max-time 120 $SOURCE_URL | bzip2 -dc | tar -tvf -" \
  "curl --range 0-$RANGE_END --max-time 120 $SOURCE_URL | bzip2 -dc | tar -xOf - README.txt" \
  > "$OUTPUT/commands.txt"

curl -I --max-time 30 -sS "$SOURCE_URL" > "$OUTPUT/headers.txt" 2> "$OUTPUT/headers.stderr.txt"
printf '%s\n' "$?" > "$OUTPUT/headers.exit_code.txt"

set +e
curl --range "0-$RANGE_END" --max-time 120 -sS "$SOURCE_URL" |
  bzip2 -dc 2> "$OUTPUT/prefix.bzip2.stderr.txt" |
  tar -tvf - > "$OUTPUT/prefix.filelist.txt" 2> "$OUTPUT/prefix.tar.stderr.txt"
prefix_status=("${PIPESTATUS[@]}")
set -e
printf 'curl=%s\nbzip2=%s\ntar=%s\n' "${prefix_status[0]}" "${prefix_status[1]}" "${prefix_status[2]}" > "$OUTPUT/prefix.pipeline.exit_codes.txt"

set +e
curl --range "0-$RANGE_END" --max-time 120 -sS "$SOURCE_URL" |
  bzip2 -dc 2> "$OUTPUT/readme.bzip2.stderr.txt" |
  tar -xOf - README.txt > "$OUTPUT/README.txt" 2> "$OUTPUT/readme.tar.stderr.txt"
readme_status=("${PIPESTATUS[@]}")
set -e
printf 'curl=%s\nbzip2=%s\ntar=%s\n' "${readme_status[0]}" "${readme_status[1]}" "${readme_status[2]}" > "$OUTPUT/readme.pipeline.exit_codes.txt"

printf '%s\n' \
  '# Exact-version source archive metadata' \
  '' \
  "- URL: $SOURCE_URL" \
  "- Bounded range: bytes 0-$RANGE_END" \
  '- The complete archive was not downloaded by this script.' \
  '- Truncated stream diagnostics are preserved and expected.' \
  '- No device or boot-chain operation was executed.' \
  > "$OUTPUT/result.md"

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote bounded metadata to %s\n' "$OUTPUT"
