#!/usr/bin/env bash
# Restore only the mutations explicitly listed in a Phase 3C plan.
#
# Plan format (tab separated, one operation per line):
#   setting          NAMESPACE KEY PRESENT|ABSENT VALUE
#   preferred        USER      COMPONENT
#   package_state    USER      PACKAGE STATE
#   component_state  USER      COMPONENT STATE
#   appops           PACKAGE   OP      MODE
#
# A setting with ABSENT is deleted. No complete settings dump is ever replayed.
# Fire Launcher package/component state and app-ops are deliberately blocked.

set -Eeuo pipefail

SERIAL=""
TEST_ID=""
PLAN=""
DRY_RUN=0
APPROVE=0

usage() {
  cat <<'EOF'
Usage:
  restore_phase3c_state.sh --serial SERIAL --test-id ID --plan FILE
       [--approve-state-change] [--dry-run]

The live command requires the exact phrase:
  APPROVE PHASE3C-RESTORE TEST-ID

Only operations in the supplied plan are executed. Unknown operation types,
unsafe package targets, and settings outside system/secure/global are rejected.
EOF
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) [ "$#" -ge 2 ] || die '--serial requires a value'; SERIAL="$2"; shift 2 ;;
    --test-id) [ "$#" -ge 2 ] || die '--test-id requires a value'; TEST_ID="$2"; shift 2 ;;
    --plan) [ "$#" -ge 2 ] || die '--plan requires a value'; PLAN="$2"; shift 2 ;;
    --approve-state-change) APPROVE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die '--serial is required'
[ -n "$TEST_ID" ] || die '--test-id is required'
[ -n "$PLAN" ] || die '--plan is required'
[ -f "$PLAN" ] || die "plan does not exist: $PLAN"

ADB=(adb -s "$SERIAL")
TEST_PACKAGE='org.fireosresearch.home.p0'

reject_fire_state() {
  local target="$1"
  case "$target" in
    com.amazon.firelauncher|com.amazon.firelauncher/*|*com.amazon.firelauncher/*)
      die "refusing Fire Launcher package/component state mutation: $target" ;;
  esac
}

reject_non_test_state() {
  local target="$1"
  case "$target" in
    "$TEST_PACKAGE"|"$TEST_PACKAGE"/*) ;;
    *) die "refusing restore state outside the Phase 3C test package: $target" ;;
  esac
}

execute_plan() {
  local op a b c d extra
  while IFS=$'\t' read -r op a b c d extra; do
    [ -n "${op:-}" ] || continue
    case "$op" in
      \#) continue ;;
      setting)
        [ -n "${a:-}" ] && [ -n "${b:-}" ] && [ -n "${c:-}" ] || die 'invalid setting plan row'
        case "$a" in system|secure|global) ;; *) die "unsupported settings namespace: $a" ;; esac
        case "$c" in
          PRESENT)
            [ -n "${d:-}" ] || die "PRESENT setting row requires a value: $a/$b"
            printf 'RESTORE settings put %s %s %s\n' "$a" "$b" "$d"
            "${ADB[@]}" shell settings put "$a" "$b" "$d"
            ;;
          ABSENT)
            printf 'RESTORE settings delete %s %s\n' "$a" "$b"
            "${ADB[@]}" shell settings delete "$a" "$b"
            ;;
          *) die "setting state must be PRESENT or ABSENT: $c" ;;
        esac
        ;;
      preferred)
        [ -n "${a:-}" ] && [ -n "${b:-}" ] || die 'invalid preferred plan row'
        printf 'RESTORE preferred HOME user=%s component=%s\n' "$a" "$b"
        "${ADB[@]}" shell cmd package set-home-activity --user "$a" "$b"
        ;;
      package_state)
        [ -n "${a:-}" ] && [ -n "${b:-}" ] && [ -n "${c:-}" ] || die 'invalid package_state plan row'
        reject_fire_state "$b"
        reject_non_test_state "$b"
        case "$c" in
          ABSENT)
            printf 'RESTORE uninstall --user %s %s\n' "$a" "$b"
            "${ADB[@]}" shell pm uninstall --user "$a" "$b"
            ;;
          ENABLED)
            printf 'RESTORE enable --user %s %s\n' "$a" "$b"
            "${ADB[@]}" shell pm enable --user "$a" "$b"
            ;;
          DISABLED_USER)
            printf 'RESTORE disable-user --user %s %s\n' "$a" "$b"
            "${ADB[@]}" shell pm disable-user --user "$a" "$b"
            ;;
          *) die "unsupported package restore state: $c" ;;
        esac
        ;;
      component_state)
        [ -n "${a:-}" ] && [ -n "${b:-}" ] && [ -n "${c:-}" ] || die 'invalid component_state plan row'
        reject_fire_state "$b"
        reject_non_test_state "$b"
        case "$c" in
          ENABLED)
            printf 'RESTORE component enable --user %s %s\n' "$a" "$b"
            "${ADB[@]}" shell pm enable --user "$a" "$b"
            ;;
          DISABLED_USER)
            printf 'RESTORE component disable-user --user %s %s\n' "$a" "$b"
            "${ADB[@]}" shell pm disable-user --user "$a" "$b"
            ;;
          DEFAULT)
            printf 'RESTORE component default --user %s %s\n' "$a" "$b"
            "${ADB[@]}" shell cmd package set-enabled-setting "$b" default --user "$a"
            ;;
          *) die "unsupported component restore state: $c" ;;
        esac
        ;;
      appops)
        [ -n "${a:-}" ] && [ -n "${b:-}" ] && [ -n "${c:-}" ] || die 'invalid appops plan row'
        reject_fire_state "$a"
        reject_non_test_state "$a"
        printf 'RESTORE appops set %s %s %s\n' "$a" "$b" "$c"
        "${ADB[@]}" shell appops set "$a" "$b" "$c"
        ;;
      *) die "unsupported restore operation: $op" ;;
    esac
  done < "$PLAN"
}

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'DRY-RUN: no ADB command will execute.\n'
  printf 'DRY-RUN: serial=%s test-id=%s plan=%s\n' "$SERIAL" "$TEST_ID" "$PLAN"
  printf 'DRY-RUN: accepted operations:\n'
  sed -n '/^[[:space:]]*#/!{/^[[:space:]]*$/!p;}' "$PLAN"
  exit 0
fi

[ "$APPROVE" -eq 1 ] || die 'live restore requires --approve-state-change'
printf 'This restores only explicit Phase 3C plan rows.\n'
printf 'Type APPROVE PHASE3C-RESTORE %s to continue: ' "$TEST_ID"
read -r approval
[ "$approval" = "APPROVE PHASE3C-RESTORE $TEST_ID" ] || die 'approval phrase did not match; no restore command was executed'

validate_devices() {
  local lines
  lines=$("${ADB[@]}" devices -l 2>/dev/null || true)
  printf '%s\n' "$lines" | awk -v serial="$SERIAL" '$1 == serial && $2 == "device" { found=1 } END { exit(found ? 0 : 1) }' || \
    die "serial is not connected in device state"
}

validate_devices
execute_plan
printf 'Phase 3C explicit restore completed: %s\n' "$TEST_ID"
