#!/usr/bin/env bash

set -u

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

timestamp_utc() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

timestamp_id() {
  date -u '+%Y%m%dT%H%M%SZ'
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

sha256_file() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    die 'neither shasum nor sha256sum is available'
  fi
}

sanitize_id() {
  printf '%s' "$1" | tr -c '[:alnum:]_.-' '_'
}

ensure_new_path() {
  [ ! -e "$1" ] || die "refusing to overwrite existing path: $1"
}

quote_arg() {
  local value="$1"
  value=${value//\'/\'\\\'\'}
  printf "'%s'" "$value"
}

render_command() {
  local arg
  local rendered=''
  for arg in "$@"; do
    if [ -n "$rendered" ]; then
      rendered="$rendered "
    fi
    rendered="$rendered$(quote_arg "$arg")"
  done
  printf '%s' "$rendered"
}

validate_serial() {
  local serial="$1"
  require_command adb

  local state
  state=$(adb -s "$serial" get-state 2>&1) || die "ADB get-state failed for serial $serial: $state"
  [ "$state" = 'device' ] || die "serial $serial is not in device state: $state"

  local count
  count=$(adb devices | awk -v wanted="$serial" '$1 == wanted && $2 == "device" { count++ } END { print count + 0 }')
  [ "$count" -eq 1 ] || die "serial $serial is not uniquely listed as a device"
}

record_manifest() {
  local manifest="$1"
  local label="$2"
  local status="$3"
  local started="$4"
  local finished="$5"
  local command_text="$6"
  local output_path="$7"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$label" "$status" "$started" "$finished" "$command_text" "$output_path" >> "$manifest"
}

run_adb_capture() {
  local label="$1"
  local required="$2"
  local output_path="$3"
  shift 3

  local started finished status command_text
  started=$(timestamp_utc)
  command_text="adb -s $(quote_arg "$ADB_SERIAL") $(render_command "$@")"

  set +e
  adb -s "$ADB_SERIAL" "$@" >"$output_path" 2>&1
  status=$?
  set -e

  finished=$(timestamp_utc)
  if [ "$status" -ne 0 ] && [ "$required" = 'yes' ]; then
    HARD_FAILURES=$((HARD_FAILURES + 1))
  fi
  record_manifest "$MANIFEST" "$label" "$status" "$started" "$finished" "$command_text" "$output_path"
  LAST_STATUS="$status"
  return 0
}

write_sha256_manifest() {
  local root="$1"
  local output="$2"
  local file relative digest

  : > "$output"
  while IFS= read -r -d '' file; do
    case "$file" in
      "$output") continue ;;
    esac
    relative=${file#"$root"/}
    digest=$(sha256_file "$file")
    printf '%s  %s\n' "$digest" "$relative" >> "$output"
  done < <(find "$root" -type f -print0)
}
