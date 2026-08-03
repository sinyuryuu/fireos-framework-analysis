#!/usr/bin/env bash
# Reproducible, offline inspection of an extracted boot-chain artifact.
# This script never contacts a device and never writes an image.

set -Eeuo pipefail

INPUT=""
OUTPUT=""
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  inspect_phase5_boot_chain_artifact.sh --input FILE --output DIR [--dry-run]

The input is treated as an immutable artifact. The output directory must not
already exist. No ADB, fastboot, MTK, exploit, or image-writing command is
used.
EOF
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --input) [ "$#" -ge 2 ] || die '--input requires a value'; INPUT="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$INPUT" ] || die '--input is required'
[ -n "$OUTPUT" ] || die '--output is required'
[ -f "$INPUT" ] || die "input is not a regular file: $INPUT"
case "$OUTPUT" in /|.|..|"") die "refusing unsafe output directory: $OUTPUT" ;; esac

commands=(
  "shasum -a 256 $INPUT"
  "file $INPUT"
  "xxd -l 256 -g 1 $INPUT"
  "strings -a -n 6 $INPUT | rg -i 'MTK_BLOADER|preloader_|PL Build|build date|DA_INFO|daa_enabled|anti.?rollback|secure|auth|trona|8183|8168|chip|hwcode|hw ver|sw ver|DA validation|LK DA'"
)

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no command will execute.\n'
  printf 'DRY-RUN: input=%s output=%s\n' "$INPUT" "$OUTPUT"
  printf 'DRY-RUN: planned offline commands:\n'
  printf '  %s\n' "${commands[@]}"
  exit 0
fi

[ ! -e "$OUTPUT" ] || die "output directory already exists; refusing to overwrite: $OUTPUT"
mkdir -p "$OUTPUT"
printf '%s\n' "${commands[@]}" > "$OUTPUT/commands.txt"
printf 'input=%s\ninput_sha256=%s\ntimestamp_utc=%s\n' \
  "$INPUT" "$(shasum -a 256 "$INPUT" | awk '{print $1}')" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
  > "$OUTPUT/metadata.tsv"

file "$INPUT" > "$OUTPUT/file.txt"
shasum -a 256 "$INPUT" > "$OUTPUT/input.sha256"
xxd -l 256 -g 1 "$INPUT" > "$OUTPUT/header.hex"
strings -a -n 6 "$INPUT" \
  | rg -i 'MTK_BLOADER|preloader_|PL Build|build date|DA_INFO|daa_enabled|anti.?rollback|secure|auth|trona|8183|8168|chip|hwcode|hw ver|sw ver|DA validation|LK DA' \
  > "$OUTPUT/strings-selected.txt" || true

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z \
  | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Offline artifact inspection written to %s\n' "$OUTPUT"
