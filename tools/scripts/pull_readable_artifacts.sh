#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

SERIAL=''
OUTPUT_DIR="$PROJECT_ROOT"
RUN_ID=''
DRY_RUN=0
PACKAGE_SPECS=()
PATH_SPECS=()

usage() {
  cat <<'EOF'
Usage: pull_readable_artifacts.sh --serial SERIAL [--output-dir PROJECT_ROOT]
       [--run-id ID] [--package PACKAGE:CATEGORY]... [--path REMOTE_PATH:CATEGORY]...
       [--dry-run]

Uses pm path and adb pull only. It never writes to the device.
Each --package may resolve multiple APKs, including splits.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial)
      [ "$#" -ge 2 ] || die '--serial requires a value'
      SERIAL="$2"
      shift 2
      ;;
    --output-dir)
      [ "$#" -ge 2 ] || die '--output-dir requires a path'
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --run-id)
      [ "$#" -ge 2 ] || die '--run-id requires a value'
      RUN_ID="$2"
      shift 2
      ;;
    --package)
      [ "$#" -ge 2 ] || die '--package requires PACKAGE:CATEGORY'
      PACKAGE_SPECS[${#PACKAGE_SPECS[@]}]="$2"
      shift 2
      ;;
    --path)
      [ "$#" -ge 2 ] || die '--path requires REMOTE_PATH:CATEGORY'
      PATH_SPECS[${#PATH_SPECS[@]}]="$2"
      shift 2
      ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ "$(( ${#PACKAGE_SPECS[@]} + ${#PATH_SPECS[@]} ))" -gt 0 ] || die 'at least one --package or --path is required'

if [ -z "$RUN_ID" ]; then
  RUN_ID="$(timestamp_id)_$(sanitize_id "$SERIAL")"
else
  RUN_ID=$(sanitize_id "$RUN_ID")
fi

MANIFEST_DIR="$OUTPUT_DIR/firmware/manifests/$RUN_ID"
MANIFEST="$MANIFEST_DIR/command_manifest.tsv"
HASHES="$MANIFEST_DIR/sha256sums.txt"

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no ADB command will be executed.\n'
  printf 'DRY-RUN: run ID=%s\n' "$RUN_ID"
  if [ -n "${PACKAGE_SPECS[*]-}" ]; then
    for spec in "${PACKAGE_SPECS[@]}"; do
      package_name=${spec%%:*}
      category=${spec#*:}
      [ "$package_name" != "$spec" ] || die "invalid --package spec: $spec"
      printf "DRY-RUN: adb -s '%s' shell pm path '%s'\n" "$SERIAL" "$package_name"
      printf 'DRY-RUN: pull resolved paths into artifacts/%s/\n' "$category"
    done
  fi
  if [ -n "${PATH_SPECS[*]-}" ]; then
    for spec in "${PATH_SPECS[@]}"; do
      remote_path=${spec%:*}
      category=${spec##*:}
      [ "$remote_path" != "$spec" ] || die "invalid --path spec: $spec"
      printf "DRY-RUN: adb -s '%s' pull '%s' 'artifacts/%s/'\n" "$SERIAL" "$remote_path" "$category"
    done
  fi
  exit 0
fi

validate_serial "$SERIAL"
ensure_new_path "$MANIFEST_DIR"
mkdir -p "$MANIFEST_DIR"
printf 'label\tstatus\tstarted_utc\tfinished_utc\tcommand\toutput\tsha256\n' > "$MANIFEST"
HARD_FAILURES=0
LAST_STATUS=0
ADB_SERIAL="$SERIAL"

record_pull() {
  local label="$1"
  local status="$2"
  local started="$3"
  local finished="$4"
  local source="$5"
  local target="$6"
  local hash="$7"
  printf '%s\t%s\t%s\t%s\tadb -s %s pull %s\t%s\t%s\n' \
    "$label" "$status" "$started" "$finished" "$(quote_arg "$SERIAL")" "$(quote_arg "$source")" "$target" "$hash" >> "$MANIFEST"
}

pull_one() {
  local remote_path="$1"
  local category="$2"
  local label="$3"
  local target_name="$4"
  local target_dir="$OUTPUT_DIR/artifacts/$category"
  local target="$target_dir/$target_name"
  local log_path="$MANIFEST_DIR/pull_${label}.log"
  local started finished status hash

  mkdir -p "$target_dir"
  ensure_new_path "$target"
  started=$(timestamp_utc)
  set +e
  adb -s "$SERIAL" pull "$remote_path" "$target" >"$log_path" 2>&1
  status=$?
  set -e
  finished=$(timestamp_utc)
  hash='-'
  if [ "$status" -eq 0 ] && [ -f "$target" ]; then
    hash=$(sha256_file "$target")
  else
    HARD_FAILURES=$((HARD_FAILURES + 1))
  fi
  record_pull "$label" "$status" "$started" "$finished" "$remote_path" "$target" "$hash"
}

if [ -n "${PACKAGE_SPECS[*]-}" ]; then
  for spec in "${PACKAGE_SPECS[@]}"; do
    package_name=${spec%%:*}
    category=${spec#*:}
    [ "$package_name" != "$spec" ] || die "invalid --package spec: $spec"
    safe_package=$(sanitize_id "$package_name")
    safe_path_file="$MANIFEST_DIR/pm_path_${safe_package}.txt"
    run_adb_capture "pm_path_$safe_package" yes "$safe_path_file" shell pm path "$package_name"
    if [ "$LAST_STATUS" -ne 0 ]; then
      continue
    fi
    index=0
    while IFS= read -r line; do
      case "$line" in
        package:*)
          remote_path=${line#package:}
          base_name=$(basename "$remote_path")
          target_name="${safe_package}__${index}_${base_name}"
          pull_one "$remote_path" "$category" "${safe_package}_${index}" "$target_name"
          index=$((index + 1))
          ;;
      esac
    done < "$safe_path_file"
  done
fi

if [ -n "${PATH_SPECS[*]-}" ]; then
  for spec in "${PATH_SPECS[@]}"; do
    remote_path=${spec%:*}
    category=${spec##*:}
    [ "$remote_path" != "$spec" ] || die "invalid --path spec: $spec"
    base_name=$(basename "$remote_path")
    safe_remote=$(sanitize_id "$remote_path")
    pull_one "$remote_path" "$category" "path_${safe_remote}" "$base_name"
  done
fi

: > "$HASHES"
awk -F '\t' 'NR > 1 && $1 !~ /^pm_path_/ && $2 == 0 && $7 != "-" { print $7 "  " $6 }' "$MANIFEST" > "$HASHES"

printf 'Artifact pull completed: %s\n' "$RUN_ID"
if [ "$HARD_FAILURES" -ne 0 ]; then
  printf 'Artifact pull completed with %s failure(s); inspect %s\n' "$HARD_FAILURES" "$MANIFEST" >&2
  exit 2
fi
