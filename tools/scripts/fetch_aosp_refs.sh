#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
# shellcheck source=common.sh
. "$SCRIPT_DIR/common.sh"

OUTPUT_ROOT="$PROJECT_ROOT/aosp/android-9"
DRY_RUN=0
TAGS=(android-9.0.0_r1 android-9.0.0_r61)

usage() {
  cat <<'EOF'
Usage: fetch_aosp_refs.sh [--output-root PATH] [--tag TAG ...] [--dry-run]

Fetches a small, explicit set of Android 9 source references from the
official android.googlesource.com repositories. It never overwrites a file.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --output-root)
      [ "$#" -ge 2 ] || die '--output-root requires a path'
      OUTPUT_ROOT="$2"
      shift 2
      ;;
    --tag)
      [ "$#" -ge 2 ] || die '--tag requires a tag'
      TAGS+=("$2")
      shift 2
      ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

# repo|path entries. Missing files are a useful AOSP-version signal and cause
# the script to stop rather than silently creating an incomplete baseline.
REFS=(
  'platform/frameworks/base|services/core/java/com/android/server/pm/PackageManagerService.java'
  'platform/frameworks/base|services/core/java/com/android/server/pm/ProtectedPackages.java'
  'platform/frameworks/base|services/core/java/com/android/server/pm/Settings.java'
  'platform/frameworks/base|services/core/java/com/android/server/pm/PackageSetting.java'
  'platform/frameworks/base|services/core/java/com/android/server/pm/PreferredActivity.java'
  'platform/frameworks/base|services/core/java/com/android/server/pm/PersistentPreferredIntentResolver.java'
  'platform/frameworks/base|services/core/java/com/android/server/policy/PhoneWindowManager.java'
  'platform/frameworks/base|services/core/java/com/android/server/am/ActivityManagerService.java'
  'platform/frameworks/base|services/core/java/com/android/server/am/ActivityStack.java'
  'platform/frameworks/base|services/core/java/com/android/server/am/ActivityStackSupervisor.java'
  'platform/frameworks/base|services/core/java/com/android/server/am/ActivityStarter.java'
  'platform/frameworks/base|services/core/java/com/android/server/wm/WindowManagerService.java'
  'platform/frameworks/base|services/core/java/com/android/server/input/InputManagerService.java'
  'platform/frameworks/base|services/devicepolicy/java/com/android/server/devicepolicy/DevicePolicyManagerService.java'
  'platform/frameworks/base|core/java/android/app/ActivityManager.java'
  'platform/frameworks/base|core/java/android/content/Intent.java'
  'platform/frameworks/base|core/java/android/content/pm/PackageManager.java'
  'platform/frameworks/base|packages/SystemUI/src/com/android/systemui/recents/RecentsActivity.java'
  'platform/packages/apps/Settings|src/com/android/settings/applications/defaultapps/DefaultHomePicker.java'
  'platform/packages/apps/Settings|src/com/android/settings/applications/defaultapps/DefaultHomePreferenceController.java'
  'platform/packages/apps/Settings|src/com/android/settings/applications/DefaultAppSettings.java'
  'platform/packages/apps/Settings|res/xml/app_default_settings.xml'
  'platform/packages/apps/Settings|res/xml/default_home_settings.xml'
)

decode_base64() {
  if base64 -D </dev/null >/dev/null 2>&1; then
    base64 -D
  else
    base64 --decode
  fi
}

fetch_ref() {
  local tag="$1"
  local entry="$2"
  local repo="${entry%%|*}"
  local relative="${entry#*|}"
  local target="$OUTPUT_ROOT/$tag/$repo/$relative"
  local url="https://android.googlesource.com/$repo/+/$tag/$relative?format=TEXT"
  if [ -e "$target" ] && [ ! -s "$target" ]; then
    rm -- "$target"
  fi
  if [ -s "$target" ]; then
    if ! grep -F -q "$(printf '%s\t%s\t%s\t' "$tag" "$repo" "$relative")" "$OUTPUT_ROOT/fetch-manifest.tsv"; then
      printf '%s\t%s\t%s\t%s\n' "$tag" "$repo" "$relative" "$(sha256sum "$target" | awk '{print $1}')" >> "$OUTPUT_ROOT/fetch-manifest.tsv"
    fi
    printf 'SKIP existing AOSP reference %s\n' "$target"
    return 0
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    printf 'DRY-RUN: fetch %s\n' "$url"
    return 0
  fi
  mkdir -p "$(dirname -- "$target")"
  sleep 1
  curl --fail --silent --show-error --location --retry 8 --retry-delay 3 --retry-max-time 90 --retry-all-errors "$url" | decode_base64 > "$target"
  [ -s "$target" ] || die "empty AOSP reference: $target"
  printf '%s\t%s\t%s\t%s\n' "$tag" "$repo" "$relative" "$(sha256sum "$target" | awk '{print $1}')" >> "$OUTPUT_ROOT/fetch-manifest.tsv"
}

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: output root %s\n' "$OUTPUT_ROOT"
else
  mkdir -p "$OUTPUT_ROOT"
  if [ ! -e "$OUTPUT_ROOT/fetch-manifest.tsv" ]; then
    printf 'tag\trepository\tpath\tsha256\n' > "$OUTPUT_ROOT/fetch-manifest.tsv"
  fi
fi

for tag in "${TAGS[@]}"; do
  for ref in "${REFS[@]}"; do
    fetch_ref "$tag" "$ref"
  done
done

if [ "$DRY_RUN" -eq 0 ]; then
  printf 'Fetched AOSP references under %s\n' "$OUTPUT_ROOT"
fi
