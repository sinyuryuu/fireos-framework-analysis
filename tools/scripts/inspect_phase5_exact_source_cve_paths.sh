#!/usr/bin/env bash
# Host-only inventory of paths in the official Fire OS source archive.
# This script never invokes adb, fastboot, BROM, DA, a loader, or downloaded
# source as executable code. It streams the bzip2/tar archive and retains only
# path names relevant to kernel-CVE applicability.
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
      printf '%s\n' 'Usage: inspect_phase5_exact_source_cve_paths.sh --url URL --output DIR [--dry-run]'
      exit 0
      ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SOURCE_URL" ] || die '--url is required'
[ -n "$OUTPUT" ] || die '--output is required'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no network request or extraction will execute.\n'
  printf 'DRY-RUN: curl --fail --retry 2 %q | bzip2 -dc | tar -tf - | filter CVE paths\n' "$SOURCE_URL"
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
  printf 'device_operation=none\n'
  printf 'downloaded_code_execution=none\n'
} > "$OUTPUT/metadata.tsv"
cat > "$OUTPUT/commands.txt" <<EOF
curl --fail --retry 2 --max-time 1800 -sS $SOURCE_URL | bzip2 -dc | tar -tf - | filter kernel CVE path names
EOF

PATTERN='rtmutex|futex|preloader|u-boot|uboot|cmdq|bluetooth|atci|ims|bootloader|bootrom'
set +e
curl --fail --retry 2 --max-time 1800 -sS "$SOURCE_URL" \
  2> "$OUTPUT/curl.stderr.txt" \
  | bzip2 -dc 2> "$OUTPUT/bzip2.stderr.txt" \
  | tar -tf - 2> "$OUTPUT/tar.stderr.txt" \
  | awk -v pattern="$PATTERN" 'tolower($0) ~ pattern { print }' \
  > "$OUTPUT/path-matches.txt"
PIPE_STATUS=("${PIPESTATUS[@]}")
set -e
printf 'curl=%s\nbzip2=%s\ntar=%s\nfilter=%s\n' \
  "${PIPE_STATUS[0]}" "${PIPE_STATUS[1]}" "${PIPE_STATUS[2]}" "${PIPE_STATUS[3]}" \
  > "$OUTPUT/pipeline-status.tsv"

sort -u "$OUTPUT/path-matches.txt" -o "$OUTPUT/path-matches.txt"
wc -l "$OUTPUT/path-matches.txt" > "$OUTPUT/path-matches.count.txt"
cat > "$OUTPUT/result.md" <<EOF
# Exact Fire OS source archive — CVE-relevant path inventory

- Source URL: $SOURCE_URL
- The archive was streamed through \`bzip2\` and \`tar -tf\`; no downloaded source
  file was executed.
- \`path-matches.txt\` contains only archive paths matching: \`$PATTERN\`.
- Pipeline exit statuses are in \`pipeline-status.tsv\`; a non-zero producer
  status is a transport/decompression result, not a vulnerability verdict.
- No ADB, fastboot, BROM, DA, loader, partition, or device operation ran.
EOF

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote exact-source CVE path inventory to %s\n' "$OUTPUT"
