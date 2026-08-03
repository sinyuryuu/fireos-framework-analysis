#!/usr/bin/env bash
# Host-only build of the bounded AArch64 CMDQ compatibility probe.
# This script never invokes adb, fastboot, BROM, DA, or the output binary.
set -Eeuo pipefail

OUTPUT=""
DRY_RUN=0
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE_C="$REPO_ROOT/tools/phase5/cmdq_compat_probe.c"
SOURCE_S="$REPO_ROOT/tools/phase5/raw_syscall_aarch64.S"

die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --output) [ "$#" -ge 2 ] || die '--output requires a value'; OUTPUT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: build_phase5h_cmdq_probe.sh --output DIR [--dry-run]'
      exit 0
      ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$OUTPUT" ] || die '--output is required'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: clang --target=aarch64-linux-android28 -ffreestanding -nostdlib ...\n'
  printf 'DRY-RUN: compile %q and %q; never execute the resulting ELF\n' "$SOURCE_C" "$SOURCE_S"
  printf 'DRY-RUN: write ELF, source hashes, tool versions, and build manifest under %q\n' "$OUTPUT"
  exit 0
fi

case "$OUTPUT" in /|.|..|""|/tmp|/var/tmp) die "unsafe output directory: $OUTPUT" ;; esac
[ ! -e "$OUTPUT" ] || die "output already exists: $OUTPUT"
command -v clang >/dev/null 2>&1 || die 'clang is required'
OBJDUMP="$(command -v llvm-objdump 2>/dev/null || true)"
[ -n "$OBJDUMP" ] || [ ! -x /Library/Developer/CommandLineTools/usr/bin/llvm-objdump ] || OBJDUMP=/Library/Developer/CommandLineTools/usr/bin/llvm-objdump
[ -n "$OBJDUMP" ] || die 'llvm-objdump is required'
LLD="$(command -v ld.lld 2>/dev/null || true)"
[ -n "$LLD" ] || [ ! -x /opt/homebrew/share/android-commandlinetools/build-tools/35.0.0/lld-bin/lld ] || LLD=/opt/homebrew/share/android-commandlinetools/build-tools/35.0.0/lld-bin/lld
[ -n "$LLD" ] || die 'ld.lld/lld is required'
command -v file >/dev/null 2>&1 || die 'file is required'
mkdir -p "$OUTPUT"

TARGET="aarch64-linux-android28"
CC=(clang --target="$TARGET")
COMMON=(-ffreestanding -fno-builtin -fno-stack-protector -fno-pic -fno-asynchronous-unwind-tables -O2)

{
  printf 'target=%s\n' "$TARGET"
  printf 'timestamp_utc=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  printf 'clang=%s\n' "$(command -v clang)"
  clang --version | head -1
} > "$OUTPUT/tool_versions.txt"
shasum -a 256 "$SOURCE_C" "$SOURCE_S" > "$OUTPUT/source.sha256"

printf '%q ' "${CC[@]}" "${COMMON[@]}" -c "$SOURCE_C" -o "$OUTPUT/probe.o" > "$OUTPUT/compile.command.txt"
printf '\n' >> "$OUTPUT/compile.command.txt"
printf '%q ' "${CC[@]}" "${COMMON[@]}" -c "$SOURCE_S" -o "$OUTPUT/syscall.o" >> "$OUTPUT/compile.command.txt"
printf '\n' >> "$OUTPUT/compile.command.txt"
printf '%q ' "$LLD" -flavor gnu -e _start --build-id=none -z norelro "$OUTPUT/probe.o" "$OUTPUT/syscall.o" -o "$OUTPUT/cmdq_compat_probe" >> "$OUTPUT/compile.command.txt"
printf '\n' >> "$OUTPUT/compile.command.txt"

"${CC[@]}" "${COMMON[@]}" -c "$SOURCE_C" -o "$OUTPUT/probe.o"
"${CC[@]}" "${COMMON[@]}" -c "$SOURCE_S" -o "$OUTPUT/syscall.o"
"$LLD" -flavor gnu -e _start --build-id=none -z norelro \
  "$OUTPUT/probe.o" "$OUTPUT/syscall.o" -o "$OUTPUT/cmdq_compat_probe"

"$OBJDUMP" -p -h -t "$OUTPUT/cmdq_compat_probe" > "$OUTPUT/objdump.txt"
"$OBJDUMP" -d --no-show-raw-insn "$OUTPUT/cmdq_compat_probe" > "$OUTPUT/disassembly.txt"
strings "$OUTPUT/cmdq_compat_probe" > "$OUTPUT/strings.txt"
file "$OUTPUT/cmdq_compat_probe" > "$OUTPUT/file.txt"

cat > "$OUTPUT/README.txt" <<EOF
This is a host-built, never-executed AArch64 probe for
CMDQ-IOCTL-V3-COMPAT-T01. It opens /dev/mtk_cmdq read-only and issues one
ioctl #7 with count=0. It contains no retry, non-zero allocation, address use,
kernel-memory primitive, root setup, or Android package logic.

The binary must not be pushed or run without the exact Level 3 approval named
in findings/phase-5h-cmdq-ioctl-compat-level3-report.md.
EOF

find "$OUTPUT" -type f ! -name sha256sums.txt -print0 | sort -z | xargs -0 shasum -a 256 > "$OUTPUT/sha256sums.txt"
printf 'Built host-only AArch64 probe under %s\n' "$OUTPUT"
