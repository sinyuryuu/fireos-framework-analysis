#!/usr/bin/env bash
# Host-only path inventory for AEE/AED/MRDUMP names in the official Fire source.
# The archive is streamed; no downloaded source file is executed or retained.
set -Eeuo pipefail
export LC_ALL=C

SOURCE_URL=""
OUTPUT=""
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --url) [ "$#" -ge 2 ] || die '--url requires a value'; SOURCE_URL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: inspect_phase5y_exact_source_aee_paths.sh --url URL --output DIR [--dry-run]'
      exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SOURCE_URL" ] || die '--url is required'
[ -n "$OUTPUT" ] || die '--output is required'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no network request, extraction, device operation, or source execution.\n'
  printf 'DRY-RUN: curl --fail --retry 2 %q | bzip2 -dc | tar -tf - | filter AEE/AED/MRDUMP names\n' "$SOURCE_URL"
  exit 0
fi

case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac
[ ! -e "$OUTPUT" ] || die "output directory already exists: $OUTPUT"
mkdir -p "$OUTPUT"
OUTPUT="$(cd "$OUTPUT" && pwd)"

STAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
{
  printf 'source_url=%s\n' "$SOURCE_URL"
  printf 'inspection_timestamp_utc=%s\n' "$STAMP"
  printf 'mode=streamed_path_inventory\n'
  printf 'device_operation=none\nsource_execution=none\n'
} > "$OUTPUT/metadata.tsv"
cat > "$OUTPUT/commands.txt" <<EOF
curl --fail --retry 2 --max-time 1800 -sS $SOURCE_URL | bzip2 -dc | tar -tf - | awk filter for AEE/AED/MRDUMP/IPANIC names
EOF

set +e
curl --fail --retry 2 --max-time 1800 -sS "$SOURCE_URL" \
  2> "$OUTPUT/curl.stderr.txt" \
  | bzip2 -dc 2> "$OUTPUT/bzip2.stderr.txt" \
  | tar -tf - 2> "$OUTPUT/tar.stderr.txt" \
  | awk 'tolower($0) ~ /aee|aed|mrdump|ipanic|aee_/ { print }' \
  > "$OUTPUT/path-matches.txt"
PIPE_STATUS=("${PIPESTATUS[@]}")
set -e
printf 'curl=%s\nbzip2=%s\ntar=%s\nfilter=%s\n' \
  "${PIPE_STATUS[0]}" "${PIPE_STATUS[1]}" "${PIPE_STATUS[2]}" "${PIPE_STATUS[3]}" \
  > "$OUTPUT/pipeline-status.tsv"

sort -u "$OUTPUT/path-matches.txt" -o "$OUTPUT/path-matches.txt"
wc -l "$OUTPUT/path-matches.txt" > "$OUTPUT/path-matches.count.txt"
cat > "$OUTPUT/result.md" <<EOF
# Exact Fire source AEE path inventory

- Source URL: $SOURCE_URL
- Archive was streamed through bzip2 and tar listing; source was not executed or retained.
- Matches are path names containing AEE/AED/MRDUMP/IPANIC terms.
- This is path evidence only; it does not prove compiled code, patch status, or device reachability.
- No ADB, fastboot, BROM, DA, loader, partition, or device operation ran.
EOF

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote AEE source path inventory to %s\n' "$OUTPUT"
