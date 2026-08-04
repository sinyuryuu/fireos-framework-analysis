#!/usr/bin/env bash
# Stream selected members from an official bzip2 source archive.
# Host-only: the archive is not stored as a whole and extracted source is never
# executed or built. No ADB, bootloader, device-node, or partition operation.
set -Eeuo pipefail
export LC_ALL=C

SOURCE_URL=""
OUTPUT=""
DRY_RUN=0
MEMBERS=()

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }
while [ "$#" -gt 0 ]; do
  case "$1" in
    --url) [ "$#" -ge 2 ] || die '--url requires a value'; SOURCE_URL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --member) [ "$#" -ge 2 ] || die '--member requires a value'; MEMBERS+=("$2"); shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: stream_extract_phase5_source_members.sh --url URL --output DIR --member PATH [--member PATH ...] [--dry-run]'
      exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done
[ -n "$SOURCE_URL" ] || die '--url is required'
[ -n "$OUTPUT" ] || die '--output is required'
[ "${#MEMBERS[@]}" -gt 0 ] || die 'at least one --member is required'
case "$OUTPUT" in /|.|..|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: stream %s through bzip2 and tar; write only selected members under %s\n' "$SOURCE_URL" "$OUTPUT"
  printf 'DRY-RUN: members=%s\n' "${MEMBERS[*]}"
  exit 0
fi
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"
mkdir -p "$OUTPUT/extracted"
OUTPUT="$(cd "$OUTPUT" && pwd)"
STAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
{
  printf 'source_url=%s\n' "$SOURCE_URL"
  printf 'timestamp_utc=%s\n' "$STAMP"
  printf 'mode=stream_selected_members_only\n'
  printf 'member_count=%s\n' "${#MEMBERS[@]}"
  printf 'device_operation=none\n'
  printf 'source_execution=none\n'
  for member in "${MEMBERS[@]}"; do printf 'member=%s\n' "$member"; done
} > "$OUTPUT/metadata.tsv"
printf 'curl --fail --retry 2 --max-time 3600 -sS %q | bzip2 -dc | tar -x -f - -C %q %s\n' \
  "$SOURCE_URL" "$OUTPUT/extracted" "${MEMBERS[*]}" > "$OUTPUT/commands.txt"

set +e
curl --fail --retry 2 --max-time 3600 -sS "$SOURCE_URL" 2> "$OUTPUT/curl.stderr.txt" \
  | bzip2 -dc 2> "$OUTPUT/bzip2.stderr.txt" \
  | tar -x -f - -C "$OUTPUT/extracted" "${MEMBERS[@]}" > "$OUTPUT/tar.stdout.txt" 2> "$OUTPUT/tar.stderr.txt"
PIPE_STATUS=("${PIPESTATUS[@]}")
set -e
printf 'curl=%s\nbzip2=%s\ntar=%s\n' "${PIPE_STATUS[0]}" "${PIPE_STATUS[1]}" "${PIPE_STATUS[2]}" > "$OUTPUT/pipeline-status.tsv"

for member in "${MEMBERS[@]}"; do
  if [ -f "$OUTPUT/extracted/$member" ]; then
    shasum -a 256 "$OUTPUT/extracted/$member" >> "$OUTPUT/member-sha256.tsv"
    wc -c "$OUTPUT/extracted/$member" >> "$OUTPUT/member-size.tsv"
  else
    printf '%s\tMISSING\n' "$member" >> "$OUTPUT/member-sha256.tsv"
    printf '%s\tMISSING\n' "$member" >> "$OUTPUT/member-size.tsv"
  fi
done

cat > "$OUTPUT/result.md" <<EOF
# Streamed exact-source member extraction

- URL: $SOURCE_URL
- Selected members only; the complete archive was not stored.
- No source was executed or built.
- No ADB, fastboot, BROM, DA, loader, device-node, or partition operation ran.
- Pipeline status is in \`pipeline-status.tsv\`.
EOF
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote selected source members to %s\n' "$OUTPUT"
