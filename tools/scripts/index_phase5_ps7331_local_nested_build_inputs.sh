#!/usr/bin/env bash
# Host-only inventory of selected paths in a local PS7331 source archive.
# The archive is read-only input. No extracted source is executed or built.
set -Eeuo pipefail
export LC_ALL=C

ARCHIVE=""
OUTPUT=""
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --archive) [ "$#" -ge 2 ] || die '--archive requires a value'; ARCHIVE="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: index_phase5_ps7331_local_nested_build_inputs.sh --archive FILE --output DIR [--dry-run]'
      exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$ARCHIVE" ] || die '--archive is required'
[ -n "$OUTPUT" ] || die '--output is required'

if [ "$DRY_RUN" -eq 1 ]; then
  printf '%s\n' 'DRY-RUN: no archive is read, no output is written, and no device operation runs.'
  printf '%s\n' 'DRY-RUN: tar -xOf ARCHIVE platform.tar | tar -tf - | path filter'
  exit 0
fi

[ -f "$ARCHIVE" ] || die "archive is not a regular file: $ARCHIVE"
case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac
[ ! -e "$OUTPUT" ] || die "output directory already exists: $OUTPUT"
mkdir -p "$OUTPUT"
OUTPUT="$(cd "$OUTPUT" && pwd)"

STAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
ARCHIVE_SHA="$(shasum -a 256 "$ARCHIVE" | awk '{print $1}')"
ARCHIVE_SIZE="$(stat -f '%z' "$ARCHIVE")"
{
  printf 'archive=%s\n' "$ARCHIVE"
  printf 'archive_sha256=%s\n' "$ARCHIVE_SHA"
  printf 'archive_size_bytes=%s\n' "$ARCHIVE_SIZE"
  printf 'timestamp_utc=%s\n' "$STAMP"
  printf 'outer_member=platform.tar\n'
  printf 'mode=local_streamed_nested_path_inventory\n'
  printf 'device_operation=none\nsource_execution=none\n'
} > "$OUTPUT/metadata.tsv"

printf '%s\n' \
  "tar -xOf $ARCHIVE platform.tar | tar -tf - | awk path filter" \
  > "$OUTPUT/commands.txt"

set +e
tar -xOf "$ARCHIVE" platform.tar \
  2> "$OUTPUT/outer-tar.stderr.txt" \
  | tar -tf - \
  2> "$OUTPUT/nested-tar.stderr.txt" \
  | awk '
      BEGIN { IGNORECASE=1 }
      /(^|\/)(patch(es)?|series|quilt)(\/|$)/ ||
      /\.(patch|diff)(\/|$)/ ||
      /(^|\/)([^\/]*(rtmutex|futex|ghostlock|proxy_owner|remove_waiter)[^\/]*)$/ ||
      /(^|\/)([^\/]*(overlay|build|config|defconfig|mk|makefile)[^\/]*)$/ &&
      /(kernel|mediatek|mt8183|trona|device\/amazon)/ {
        print
      }
    ' > "$OUTPUT/matching-paths.txt"
PIPE_STATUS=("${PIPESTATUS[@]}")
set -e
printf 'outer_tar=%s\nnested_tar=%s\nfilter=%s\n' \
  "${PIPE_STATUS[0]}" "${PIPE_STATUS[1]}" "${PIPE_STATUS[2]}" \
  > "$OUTPUT/pipeline-status.tsv"

sort -u "$OUTPUT/matching-paths.txt" -o "$OUTPUT/matching-paths.txt"
wc -l "$OUTPUT/matching-paths.txt" > "$OUTPUT/matching-paths.count.txt"
rg -i '(^|/)(patch(es)?|series|quilt)(/|$)|\.(patch|diff)$' \
  "$OUTPUT/matching-paths.txt" | sort -u > "$OUTPUT/patch-diff-series-paths.txt" || true
rg -i 'rtmutex|futex|ghostlock|proxy_owner|remove_waiter' \
  "$OUTPUT/matching-paths.txt" | sort -u > "$OUTPUT/rtmutex-futex-paths.txt" || true
rg -i '(^|/)(build|config|defconfig|mk|makefile)(/|$)|(^|/)[^/]*(build|config|defconfig|mk|makefile)[^/]*$' \
  "$OUTPUT/matching-paths.txt" | sort -u > "$OUTPUT/build-config-paths.txt" || true

cat > "$OUTPUT/result.md" <<EOF
# PS7331 local nested build-input inventory

- Archive: $ARCHIVE
- Archive SHA-256: $ARCHIVE_SHA
- Archive size: $ARCHIVE_SIZE bytes
- Outer member: platform.tar
- The nested archive was listed through a local streaming pipeline; no source
  file was executed, built, or written back to the archive.
- The match files are path-name inventories only. An absent name does not prove
  that an unlabelled generated transformation is absent from the build system.
- No ADB, fastboot, BROM, DA, loader, device-node, or partition operation ran.
EOF

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote local PS7331 nested path inventory to %s\n' "$OUTPUT"
