#!/usr/bin/env bash
# Index selected names inside the platform.tar member of an official bzip2
# source archive. Host-only: no source is executed or built; no device I/O.
set -Eeuo pipefail
export LC_ALL=C

SOURCE_URL=""
OUTPUT=""
PATTERN='(^|/)(rtmutex\.c|rtmutex_common\.h|futex\.c|sched\.h|mt8183_defconfig|ion\.c|ion_drv\.c|cmdq_driver\.c)$'
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }
while [ "$#" -gt 0 ]; do
  case "$1" in
    --url) [ "$#" -ge 2 ] || die '--url requires a value'; SOURCE_URL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --pattern) [ "$#" -ge 2 ] || die '--pattern requires a value'; PATTERN="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: index_phase5_nested_platform_members.sh --url URL --output DIR [--pattern REGEX] [--dry-run]'
      exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done
[ -n "$SOURCE_URL" ] || die '--url is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in /|.|..|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: stream outer bzip2 archive, extract platform.tar, list nested members matching %s\n' "$PATTERN"
  printf 'DRY-RUN: output=%s\n' "$OUTPUT"
  exit 0
fi
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"
mkdir -p "$OUTPUT"
OUTPUT="$(cd "$OUTPUT" && pwd)"
STAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
{
  printf 'source_url=%s\n' "$SOURCE_URL"
  printf 'timestamp_utc=%s\n' "$STAMP"
  printf 'outer_member=platform.tar\n'
  printf 'nested_pattern=%s\n' "$PATTERN"
  printf 'device_operation=none\nsource_execution=none\n'
} > "$OUTPUT/metadata.tsv"
printf 'curl --fail --retry 2 --max-time 3600 -sS %q | bzip2 -dc | tar -xOf - platform.tar | tar -tf - | rg -i %q\n' "$SOURCE_URL" "$PATTERN" > "$OUTPUT/commands.txt"

set +e
curl --fail --retry 2 --max-time 3600 -sS "$SOURCE_URL" 2> "$OUTPUT/curl.stderr.txt" \
  | bzip2 -dc 2> "$OUTPUT/bzip2.stderr.txt" \
  | tar -xOf - platform.tar 2> "$OUTPUT/outer-tar.stderr.txt" \
  | tar -tf - 2> "$OUTPUT/nested-tar.stderr.txt" \
  | rg -i "$PATTERN" > "$OUTPUT/relevant-paths.txt"
PIPE_STATUS=("${PIPESTATUS[@]}")
set -e
printf 'curl=%s\nbzip2=%s\nouter_tar=%s\nnested_tar=%s\nrg=%s\n' \
  "${PIPE_STATUS[0]}" "${PIPE_STATUS[1]}" "${PIPE_STATUS[2]}" "${PIPE_STATUS[3]}" "${PIPE_STATUS[4]}" \
  > "$OUTPUT/pipeline.status.txt"

cat > "$OUTPUT/result.md" <<EOF
# Nested platform.tar member index

- URL: $SOURCE_URL
- Outer member: \`platform.tar\`
- Pattern: \`$PATTERN\`
- The nested source was listed only; no source was executed or built.
- No ADB, fastboot, BROM, DA, loader, device-node, or partition operation ran.
- Pipeline status is in \`pipeline.status.txt\`.
EOF
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote nested member index to %s\n' "$OUTPUT"
