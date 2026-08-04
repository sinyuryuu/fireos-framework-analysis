#!/usr/bin/env bash
# Host-only path inventory for possible PS7331 kernel build patches/overlays.
# It streams the official outer archive and nested platform.tar, records only
# matching path names, and never extracts or executes source.
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
      printf '%s\n' 'Usage: index_phase5_ps7331_nested_build_patches.sh --url URL --output DIR [--dry-run]'
      exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SOURCE_URL" ] || die '--url is required'
[ -n "$OUTPUT" ] || die '--output is required'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no network request, extraction, device operation, or source execution.\n'
  printf 'DRY-RUN: curl | bzip2 -dc | tar -xOf - platform.tar | tar -tf - | path filter\n'
  exit 0
fi

case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac
[ ! -e "$OUTPUT" ] || die "output directory already exists: $OUTPUT"
mkdir -p "$OUTPUT"
OUTPUT="$(cd "$OUTPUT" && pwd)"

STAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
{
  printf 'source_url=%s\n' "$SOURCE_URL"
  printf 'timestamp_utc=%s\n' "$STAMP"
  printf 'outer_member=platform.tar\n'
  printf 'mode=streamed_nested_path_inventory\n'
  printf 'device_operation=none\nsource_execution=none\n'
} > "$OUTPUT/metadata.tsv"

printf '%s\n' \
  "curl --fail --retry 2 --max-time 3600 -sS $SOURCE_URL | bzip2 -dc | tar -xOf - platform.tar | tar -tf - | awk path filter" \
  > "$OUTPUT/commands.txt"

set +e
curl --fail --retry 2 --max-time 3600 -sS "$SOURCE_URL" \
  2> "$OUTPUT/curl.stderr.txt" \
  | bzip2 -dc 2> "$OUTPUT/bzip2.stderr.txt" \
  | tar -xOf - platform.tar 2> "$OUTPUT/outer-tar.stderr.txt" \
  | tar -tf - 2> "$OUTPUT/nested-tar.stderr.txt" \
  | awk '
      BEGIN { IGNORECASE=1 }
      /(^|\/)patch(es)?(\/|$)/ ||
      /\.(patch|diff)(\/|$)/ ||
      /(^|\/)(series|quilt)(\/|$)/ ||
      /(^|\/)([^\/]*(rtmutex|futex|ghostlock|proxy_owner|remove_waiter)[^\/]*)$/ ||
      /(^|\/)([^\/]*(overlay|build|config|defconfig)[^\/]*)$/ &&
      /(kernel|mediatek|mt8183|trona)/ {
        print
      }
    ' > "$OUTPUT/matching-paths.txt"
PIPE_STATUS=("${PIPESTATUS[@]}")
set -e
printf 'curl=%s\nbzip2=%s\nouter_tar=%s\nnested_tar=%s\nfilter=%s\n' \
  "${PIPE_STATUS[0]}" "${PIPE_STATUS[1]}" "${PIPE_STATUS[2]}" \
  "${PIPE_STATUS[3]}" "${PIPE_STATUS[4]}" > "$OUTPUT/pipeline-status.tsv"

sort -u "$OUTPUT/matching-paths.txt" -o "$OUTPUT/matching-paths.txt"
wc -l "$OUTPUT/matching-paths.txt" > "$OUTPUT/matching-paths.count.txt"
rg -i '(^|/)(patch(es)?|series|quilt)(/|$)|\.(patch|diff)$' \
  "$OUTPUT/matching-paths.txt" | sort -u > "$OUTPUT/patch-diff-series-paths.txt" || true

cat > "$OUTPUT/result.md" <<EOF
# PS7331 nested build patch/overlay path inventory

- URL: $SOURCE_URL
- Outer member: platform.tar
- The nested archive was listed through a streaming pipeline; no source file
  was extracted, executed, or built.
- matching-paths.txt contains path names matching patch, overlay, build,
  kernel configuration, rtmutex/futex, or GhostLock-related terms.
- An empty match file means no matching path name was observed in this
  inventory; it does not prove that an unlabelled generated transformation is
  absent from the build environment.
- No ADB, fastboot, BROM, DA, loader, device-node, or partition operation ran.
EOF

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Wrote nested build patch/overlay path inventory to %s\n' "$OUTPUT"
