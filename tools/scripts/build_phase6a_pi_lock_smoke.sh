#!/bin/sh
set -eu

usage() {
  echo "usage: $0 [--dry-run] --output OUTPUT" >&2
  exit 2
}

dry_run=0
output=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) dry_run=1 ;;
    --output)
      shift
      [ "$#" -gt 0 ] || usage
      output=$1
      ;;
    *) usage ;;
  esac
  shift
done

[ -n "$output" ] || usage
source_file="$(CDPATH= cd -- "$(dirname -- "$0")/../test-phase6a" && pwd)/pi_lock_smoke.c"

if [ "$dry_run" -eq 1 ]; then
  printf '%s\n' "DRY-RUN: no compiler or device command will run."
  printf '%s\n' "DRY-RUN: source=$source_file"
  printf '%s\n' "DRY-RUN: output=$output"
  exit 0
fi

[ ! -e "$output" ] || {
  echo "refusing to overwrite existing output: $output" >&2
  exit 1
}

if ! command -v ld.lld >/dev/null 2>&1; then
  echo "BUILD_TOOLCHAIN_UNAVAILABLE: ld.lld is not installed or not on PATH" >&2
  exit 3
fi

mkdir -p "$(dirname -- "$output")"
clang \
  --target=aarch64-linux-android28 \
  -march=armv8-a \
  -O2 \
  -ffreestanding \
  -fno-builtin \
  -fno-stack-protector \
  -fno-pie \
  -nostdlib \
  -nodefaultlibs \
  -nostartfiles \
  -static \
  -Wl,-e,_start \
  "$source_file" \
  -o "$output"
