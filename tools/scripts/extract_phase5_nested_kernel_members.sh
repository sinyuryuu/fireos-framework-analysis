#!/usr/bin/env bash
# Host-only extraction of selected files from nested platform.tar.
# The extracted source is never built or executed and no device I/O occurs.
set -Eeuo pipefail
export LC_ALL=C

if [ "${1:-}" = "--dry-run" ]; then
  printf '%s\n' 'DRY-RUN: extract selected PS7331 kernel source members from nested platform.tar'
  exit 0
fi
[ "$#" -eq 2 ] || { printf 'Usage: %s SOURCE_URL OUTPUT_DIR\n' "$0" >&2; exit 2; }
URL="$1"
OUT="$2"
case "$OUT" in /|.|..|/tmp|/var/tmp) printf 'unsafe output directory\n' >&2; exit 2 ;; esac
[ ! -e "$OUT" ] || { printf 'output already exists: %s\n' "$OUT" >&2; exit 2; }
mkdir -p "$OUT/extracted"

printf 'source_url=%s\nouter_member=platform.tar\ndevice_operation=none\nsource_execution=none\n' "$URL" > "$OUT/metadata.tsv"
curl --fail --retry 2 --max-time 3600 -sS "$URL" \
  | bzip2 -dc \
  | tar -xOf - platform.tar \
  | tar -x -f - -C "$OUT/extracted" \
      kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c \
      kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex_common.h \
      kernel/mediatek/mt8183/4.4/kernel/futex.c \
      kernel/mediatek/mt8183/4.4/include/linux/sched.h \
      kernel/mediatek/4.4/kernel/locking/rtmutex.c \
      kernel/mediatek/4.4/kernel/locking/rtmutex_common.h \
      kernel/mediatek/4.4/kernel/futex.c \
      kernel/mediatek/4.4/include/linux/sched.h

find "$OUT/extracted" -type f -print0 | sort -z | xargs -0 shasum -a 256 > "$OUT/member-sha256.tsv"
printf '%s\n' 'source_executed=0' 'device_operation=none' 'selected_members=8' > "$OUT/result.md"
printf 'Wrote selected nested kernel members to %s\n' "$OUT"
