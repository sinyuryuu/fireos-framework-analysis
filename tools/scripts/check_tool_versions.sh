#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

DRY_RUN=0
OUTPUT="$PROJECT_ROOT/tools/tool_versions.txt"

usage() {
  cat <<'EOF'
Usage: check_tool_versions.sh [--dry-run] [--output PATH]

Checks available analysis tools without installing anything.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --output)
      [ "$#" -ge 2 ] || die '--output requires a path'
      OUTPUT="$2"
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

TOOL_NAMES='adb java python3 rg diff git jadx apktool baksmali smali d2j-dex2jar sqlite3 aapt2 apkanalyzer bundletool payload-dumper-go simg2img lpunpack unzip 7z file strings readelf objdump shasum sha256sum brotli debugfs vdexExtractor'

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: would write tool inventory to %s\n' "$OUTPUT"
  for tool in $TOOL_NAMES; do
    printf 'DRY-RUN: inspect %s\n' "$tool"
  done
  exit 0
fi

ensure_new_path "$OUTPUT"
mkdir -p "$(dirname -- "$OUTPUT")"

version_for() {
  local tool="$1"
  local path="$2"
  local output
  set +e
  case "$tool" in
    adb) output=$("$path" version 2>&1 | sed -n '1p') ;;
    java) output=$("$path" --version 2>&1 | sed -n '1p') ;;
    python3|rg|diff|git|jadx|sqlite3|file|objdump|shasum|sha256sum) output=$("$path" --version 2>&1 | sed -n '1p') ;;
    apktool|baksmali|smali|d2j-dex2jar|aapt2|bundletool|payload-dumper-go|simg2img|lpunpack) output=$("$path" --version 2>&1 | sed -n '1p') ;;
    apkanalyzer) output=$("$path" version 2>&1 | sed -n '1p') ;;
    unzip) output=$("$path" -v 2>&1 | sed -n '1p') ;;
    7z) output=$("$path" --help 2>&1 | sed -n '1p') ;;
    strings) output=$("$path" -h 2>&1 | sed -n '1p') ;;
    readelf) output=$("$path" --version 2>&1 | sed -n '1p') ;;
    brotli) output=$("$path" --version 2>&1 | sed -n '1p') ;;
    debugfs) output=$("$path" -V 2>&1 | sed -n '1p') ;;
    vdexExtractor) output=$("$path" --help 2>&1 | sed -n '1p') ;;
    *) output='' ;;
  esac
  local status=$?
  set -e
  if [ -z "$output" ]; then
    output='version output unavailable'
  fi
  printf '%s\t%s\n' "$status" "$output"
}

resolve_tool_path() {
  local tool="$1"
  local path
  if path=$(command -v "$tool" 2>/dev/null); then
    printf '%s\n' "$path"
    return 0
  fi
  case "$tool" in
    debugfs)
      [ -x /opt/homebrew/opt/e2fsprogs/sbin/debugfs ] || return 1
      printf '%s\n' /opt/homebrew/opt/e2fsprogs/sbin/debugfs
      ;;
    vdexExtractor)
      [ -x "$PROJECT_ROOT/tools/third-party/vdexExtractor/bin/vdexExtractor" ] || return 1
      printf '%s\n' "$PROJECT_ROOT/tools/third-party/vdexExtractor/bin/vdexExtractor"
      ;;
    *) return 1 ;;
  esac
}

source_for() {
  case "$1" in
    /usr/bin/*|/bin/*|/usr/sbin/*|/sbin/*|/usr/libexec/*) printf 'system\n' ;;
    /opt/homebrew/*|/usr/local/*) printf 'Homebrew-or-local-PATH\n' ;;
    *) printf 'PATH/unknown\n' ;;
  esac
}

required_for() {
  case "$1" in
    adb|python3|rg|shasum|sha256sum) printf 'required-for-initial-phase\n' ;;
    *) printf 'recommended-or-later-phase\n' ;;
  esac
}

{
  printf '# Tool Inventory\n\n'
  printf 'Checked at (UTC): %s\n' "$(timestamp_utc)"
  printf 'Project root: %s\n\n' "$PROJECT_ROOT"
  printf '| Tool | Requirement | Status | Version output | Path | Source |\n'
  printf '|---|---|---|---|---|---|\n'

  for tool in $TOOL_NAMES; do
    requirement=$(required_for "$tool")
    if path=$(resolve_tool_path "$tool"); then
      version_record=$(version_for "$tool" "$path")
      version_status=${version_record%%$'\t'*}
      version_output=${version_record#*$'\t'}
      if [ "$version_status" -eq 0 ]; then
        status='AVAILABLE'
      else
        status='UNUSABLE'
      fi
      source=$(source_for "$path")
    else
      status='MISSING'
      version_output='not found on PATH'
      path='-'
      source='-'
    fi
    version_output=${version_output//|/\\|}
    printf '| %s | %s | %s | %s | `%s` | %s |\n' \
      "$tool" "$requirement" "$status" "$version_output" "$path" "$source"
  done
} > "$OUTPUT"

printf 'Wrote %s\n' "$OUTPUT"
