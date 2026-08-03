#!/usr/bin/env bash
# Pull a bounded set of MTK userspace libraries for offline inspection.
# Read-only: no pulled file is executed and no device node is opened.
set -Eeuo pipefail
export LC_ALL=C

SERIAL=""
OUTPUT=""
DRY_RUN=0

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: pull_phase5m_mtk_userspace_artifacts.sh --serial SERIAL --output DIR [--dry-run]'
      exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$OUTPUT" ] || die '--output is required'
case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac

REMOTES=(
  /system/lib64/libion.so
  /vendor/lib64/libion_mtk.so
  /vendor/lib64/libion_ulit.so
  /system/lib64/libmtk_drvb_sys.so
  /system/lib64/libbluetooth.so
  /system/lib64/libbluetooth-binder.so
  /system/lib64/android.hardware.bluetooth@1.0.so
)

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no pull or device write; pulled files would be inspected offline only.\n'
  printf 'DRY-RUN: serial=%s output=%s\n' "$SERIAL" "$OUTPUT"
  printf '%s\n' "${REMOTES[@]}"
  exit 0
fi

command -v adb >/dev/null 2>&1 || die 'adb is required'
command -v shasum >/dev/null 2>&1 || die 'shasum is required'
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"
mkdir -p "$OUTPUT/files" "$OUTPUT/metadata"

printf 'test_id=%s\nserial=%s\nstart_utc=%s\nmode=read-only-pull\n' \
  "$(basename "$OUTPUT")" "$SERIAL" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$OUTPUT/metadata.txt"
printf '%s\n' "${REMOTES[@]}" > "$OUTPUT/remote-files.txt"

for remote in "${REMOTES[@]}"; do
  name="$(basename "$remote")"
  adb -s "$SERIAL" shell ls -lZ "$remote" > "$OUTPUT/metadata/$name.ls.stdout.txt" 2> "$OUTPUT/metadata/$name.ls.stderr.txt" || true
  adb -s "$SERIAL" shell sha256sum "$remote" > "$OUTPUT/metadata/$name.remote-sha256.stdout.txt" 2> "$OUTPUT/metadata/$name.remote-sha256.stderr.txt" || true
  adb -s "$SERIAL" pull "$remote" "$OUTPUT/files/" > "$OUTPUT/metadata/$name.pull.stdout.txt" 2> "$OUTPUT/metadata/$name.pull.stderr.txt" || true
done

for file in "$OUTPUT"/files/*; do
  [ -f "$file" ] || continue
  base="$(basename "$file")"
  file "$file" > "$OUTPUT/metadata/$base.file.txt" 2>&1 || true
  if command -v readelf >/dev/null 2>&1; then
    readelf -h "$file" > "$OUTPUT/metadata/$base.readelf-header.txt" 2>&1 || true
    readelf -S "$file" > "$OUTPUT/metadata/$base.readelf-sections.txt" 2>&1 || true
  fi
  strings -a "$file" | rg -i 'ion|sram|genie|cmdq|ioctl|bluetooth|hci|permission|selinux|mediatek' \
    > "$OUTPUT/metadata/$base.focused-strings.txt" || true
done

printf 'end_utc=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> "$OUTPUT/metadata.txt"
find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
