#!/usr/bin/env bash
set -u

# Fetch only official AOSP system/core init anchor files for offline
# comparison. It never contacts a device and refuses to overwrite files.

usage() {
  printf '%s\n' "Usage: $0 --output DIR [--dry-run]"
}

output=""
dry_run=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --output) output="$2"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$output" ]; then
  usage >&2
  exit 2
fi

if [ "$dry_run" -eq 1 ]; then
  printf '%s\n' '{"dry_run":true,"official_source":"android.googlesource.com","device_contacted":false,"files_written":false}'
  exit 0
fi

if [ -e "$output" ]; then
  printf 'refusing to overwrite existing output: %s\n' "$output" >&2
  exit 3
fi

command -v curl >/dev/null 2>&1 || { printf 'curl not found\n' >&2; exit 4; }
command -v base64 >/dev/null 2>&1 || { printf 'base64 not found\n' >&2; exit 4; }

mkdir -p "$output"
printf 'source=official android.googlesource.com/platform/system/core\n' > "$output/source-manifest.tsv"
printf 'tag\tpath\turl\tsha256\n' >> "$output/source-manifest.tsv"

tags='android-9.0.0_r1 android-9.0.0_r61'
paths='init/selinux.cpp init/selinux.h init/Android.bp init/main.cpp'

for tag in $tags; do
  for path in $paths; do
    destination="$output/$tag/$path"
    mkdir -p "$(dirname "$destination")"
    url="https://android.googlesource.com/platform/system/core/+/$tag/$path?format=TEXT"
    if ! curl --fail --silent --show-error --location "$url" | base64 --decode > "$destination"; then
      printf 'fetch failed: %s\n' "$url" >&2
      exit 5
    fi
    digest="$(shasum -a 256 "$destination" | awk '{print $1}')"
    printf '%s\t%s\t%s\t%s\n' "$tag" "$path" "$url" "$digest" >> "$output/source-manifest.tsv"
  done
done

shasum -a 256 "$output"/android-9.0.0_r1/init/* "$output"/android-9.0.0_r61/init/* > "$output/sha256sums.txt"
printf 'output=%s\ndevice_contacted=false\n' "$output"
