#!/usr/bin/env bash
# Scan a bounded range of the exact Fire OS source archive for CMDQ source.
# Host-side only: this script never invokes adb, fastboot, BROM, DA, or a
# downloaded executable. The range is intentionally bounded because the
# archive is multi-gigabyte and some HTTP paths cap range responses.
set -Eeuo pipefail
export LC_ALL=C

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
      printf '%s\n' 'Usage: scan_phase5_exact_source_cmdq.sh --url URL --output DIR --range-start BYTES --range-end BYTES [--dry-run]'
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
  printf 'DRY-RUN: no network request or decompression will execute.\n'
  printf 'DRY-RUN: curl --range %s-%s %q -o %q\n' "$RANGE_START" "$RANGE_END" "$SOURCE_URL" "$OUTPUT/source-tail.range"
  printf '%s\n' 'DRY-RUN: bzip2recover source-tail.range; bzip2 -dc each recovered block; strings; search CMDQ markers'
  exit 0
fi

case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac
[ ! -e "$OUTPUT" ] || die "output directory already exists: $OUTPUT"
mkdir -p "$OUTPUT"
OUTPUT="$(cd "$OUTPUT" && pwd)"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/phase5-source-cmdq.XXXXXX")"
trap 'rm -rf -- "$WORK_DIR"' EXIT

REQUESTED_BYTES=$((RANGE_END - RANGE_START + 1))
STAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
{
  printf 'source_url=%s\n' "$SOURCE_URL"
  printf 'requested_range=bytes=%s-%s\n' "$RANGE_START" "$RANGE_END"
  printf 'requested_bytes=%s\n' "$REQUESTED_BYTES"
  printf 'scan_timestamp_utc=%s\n' "$STAMP"
} > "$OUTPUT/metadata.tsv"
cat > "$OUTPUT/commands.txt" <<EOF
curl --fail --retry 2 --max-time 300 --range $RANGE_START-$RANGE_END $SOURCE_URL -o $OUTPUT/source-tail.range
bzip2recover source-tail.range
bzip2 -dc each recovered block | strings -n 4 | search CMDQ markers
EOF

set +e
curl --fail --retry 2 --max-time 300 -sS --range "$RANGE_START-$RANGE_END" \
  "$SOURCE_URL" -o "$OUTPUT/source-tail.range" 2> "$OUTPUT/curl.stderr.txt"
CURL_STATUS=$?
set -e
printf '%s\n' "$CURL_STATUS" > "$OUTPUT/curl.exit_code.txt"

ACTUAL_BYTES="$(wc -c < "$OUTPUT/source-tail.range" | tr -d ' ')"
printf 'actual_bytes=%s\n' "$ACTUAL_BYTES" >> "$OUTPUT/metadata.tsv"
printf 'curl_exit=%s\nrequested_bytes=%s\nactual_bytes=%s\n' \
  "$CURL_STATUS" "$REQUESTED_BYTES" "$ACTUAL_BYTES" > "$OUTPUT/transfer-summary.tsv"
shasum -a 256 "$OUTPUT/source-tail.range" > "$OUTPUT/source-tail.range.sha256"
wc -c "$OUTPUT/source-tail.range" > "$OUTPUT/source-tail.range.size.txt"

if [ "$CURL_STATUS" -ne 0 ] || [ "$ACTUAL_BYTES" -eq 0 ]; then
  cat > "$OUTPUT/result.md" <<EOF
# Exact-version CMDQ source range scan

- URL: $SOURCE_URL
- Requested range: bytes $RANGE_START-$RANGE_END ($REQUESTED_BYTES bytes)
- Actual bytes received: $ACTUAL_BYTES
- curl exit code: $CURL_STATUS

The transfer did not produce a usable range, so no bzip2 recovery or source
claim was made. This is a transport result, not evidence about the source
tree.
EOF
  find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
  exit 0
fi

cp "$OUTPUT/source-tail.range" "$WORK_DIR/source-tail.range"
(
  cd "$WORK_DIR"
  bzip2recover source-tail.range > "$OUTPUT/bzip2recover.stdout.txt" 2> "$OUTPUT/bzip2recover.stderr.txt"
)
printf '%s\n' "$?" > "$OUTPUT/bzip2recover.exit_code.txt"
find "$WORK_DIR" -maxdepth 1 -type f -name 'rec*' -print | sort > "$OUTPUT/recovered-blocks.list.txt"
printf 'recovered_blocks=%s\n' "$(wc -l < "$OUTPUT/recovered-blocks.list.txt" | tr -d ' ')" > "$OUTPUT/recovered-blocks.count.txt"

MATCHES="$OUTPUT/cmdq-source-matches.txt"
BLOCKS="$OUTPUT/cmdq-block-matches.tsv"
: > "$MATCHES"
printf 'block\tmatch_count\tfirst_matches\n' > "$BLOCKS"

MATCH_PATTERN='cmdq|mtk[-_]?cmdq|CMDQ_IOCTL|ALLOC_WRITE_ADDRESS|drivers/misc/mediatek/.{0,100}cmdq|mediatek/.{0,100}cmdq'
MAX_WORKERS="${PHASE5_SOURCE_SCAN_WORKERS:-8}"
[[ "$MAX_WORKERS" =~ ^[1-9][0-9]*$ ]] || die 'PHASE5_SOURCE_SCAN_WORKERS must be a positive integer'
PIDS=()
for recovered in "$WORK_DIR"/rec*; do
  [ -f "$recovered" ] || continue
  block_name="$(basename "$recovered")"
  block_matches="$WORK_DIR/$block_name.matches"
  (
    bzip2 -dc "$recovered" 2>/dev/null | strings -n 4 | rg -i "$MATCH_PATTERN" > "$block_matches" || true
  ) &
  PIDS+=("$!")
  if [ "${#PIDS[@]}" -ge "$MAX_WORKERS" ]; then
    for pid in "${PIDS[@]}"; do wait "$pid" || true; done
    PIDS=()
  fi
done
for pid in "${PIDS[@]}"; do wait "$pid" || true; done

for recovered in "$WORK_DIR"/rec*; do
  [ -f "$recovered" ] || continue
  block_name="$(basename "$recovered")"
  block_matches="$WORK_DIR/$block_name.matches"
  [ -f "$block_matches" ] || continue
  if [ -s "$block_matches" ]; then
    count="$(wc -l < "$block_matches" | tr -d ' ')"
    first="$(head -n 12 "$block_matches" | tr '\n' ' ' | sed 's/[[:cntrl:]]//g')"
    printf '%s\t%s\t%s\n' "$block_name" "$count" "$first" >> "$BLOCKS"
    {
      printf '## %s\n' "$block_name"
      cat "$block_matches"
    } >> "$MATCHES"
  fi
done

sort -u "$MATCHES" -o "$MATCHES"

cat > "$OUTPUT/result.md" <<EOF
# Exact-version CMDQ source range scan

- URL: $SOURCE_URL
- Requested range: bytes $RANGE_START-$RANGE_END ($REQUESTED_BYTES bytes)
- Actual bytes received: $ACTUAL_BYTES
- curl exit code: $CURL_STATUS
- Recovered bzip2 blocks: $(wc -l < "$OUTPUT/recovered-blocks.list.txt" | tr -d ' ')

Each recovered block was independently decompressed before strings and
keyword search. Raw strings on compressed rec* files was intentionally not
used. cmdq-source-matches.txt is the compact match output; an empty file is
an observation about this sampled range only, not the complete archive.

No device, ADB, fastboot, BROM, DA, loader, payload, or partition operation ran.
EOF

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote exact-source CMDQ scan to %s\n' "$OUTPUT"
