#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

IMAGE=''
OUTPUT=''
DRY_RUN=0
PATHS=(
  /system/framework/framework-res.apk
  /system/framework/framework.jar
  /system/framework/services.jar
  /system/framework/fosframework.jar
  /system/framework/fosservices.jar
  /system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk
  /system/priv-app/TabletSystemUI/TabletSystemUI.apk
  /system/priv-app/TabletSettings/TabletSettings.apk
  /system/priv-app/SettingsProvider/SettingsProvider.apk
)

usage() {
  cat <<'EOF'
Usage: extract_ext4_paths.sh --image IMAGE --output DIR [--path EXT4_PATH ...]
       [--clear-defaults] [--dry-run]

Extracts explicit files from a derived ext4 system image with debugfs. The
image is read-only and output files are never overwritten.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --image)
      [ "$#" -ge 2 ] || die '--image requires a path'
      IMAGE="$2"
      shift 2
      ;;
    --output)
      [ "$#" -ge 2 ] || die '--output requires a directory'
      OUTPUT="$2"
      shift 2
      ;;
    --path)
      [ "$#" -ge 2 ] || die '--path requires an ext4 path'
      PATHS+=("$2")
      shift 2
      ;;
    --clear-defaults) PATHS=(); shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$IMAGE" ] || die '--image is required'
[ -n "$OUTPUT" ] || die '--output is required'
[ -f "$IMAGE" ] || die "image is not a file: $IMAGE"
DEBUGFS=$(command -v debugfs 2>/dev/null || true)
if [ -z "$DEBUGFS" ]; then
  if [ -x /opt/homebrew/opt/e2fsprogs/sbin/debugfs ]; then
    DEBUGFS=/opt/homebrew/opt/e2fsprogs/sbin/debugfs
  elif [ -x /usr/local/opt/e2fsprogs/sbin/debugfs ]; then
    DEBUGFS=/usr/local/opt/e2fsprogs/sbin/debugfs
  else
    die 'debugfs is required; install e2fsprogs or provide it on PATH'
  fi
fi

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: read-only image %s\n' "$(CDPATH= cd -- "$(dirname -- "$IMAGE")" && pwd)/$(basename -- "$IMAGE")"
  printf 'DRY-RUN: output directory %s\n' "$OUTPUT"
  for ext4_path in "${PATHS[@]}"; do
    printf 'DRY-RUN: dump %s\n' "$ext4_path"
  done
  exit 0
fi

mkdir -p "$OUTPUT"
MANIFEST="$OUTPUT/extraction-manifest.tsv"
ensure_new_path "$MANIFEST"
printf 'ext4_path\toutput\tsha256\n' > "$MANIFEST"

for ext4_path in "${PATHS[@]}"; do
  [ "${ext4_path#/}" != "$ext4_path" ] || die "ext4 path must be absolute: $ext4_path"
  relative=${ext4_path#/}
  target="$OUTPUT/$relative"
  mkdir -p "$(dirname -- "$target")"
  ensure_new_path "$target"
  "$DEBUGFS" -R "dump $ext4_path $target" "$IMAGE" >/dev/null
  [ -s "$target" ] || die "debugfs produced no data for $ext4_path"
  printf '%s\t%s\t%s\n' "$ext4_path" "$target" "$(sha256sum "$target" | awk '{print $1}')" >> "$MANIFEST"
done

sha256sum "$MANIFEST" > "$OUTPUT/manifest.sha256"
printf 'Extracted %s paths under %s\n' "${#PATHS[@]}" "$OUTPUT"
