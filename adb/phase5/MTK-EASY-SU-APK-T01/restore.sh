#!/usr/bin/env bash
# Explicit rollback for MTK-EASY-SU-APK-T01.
# This script only removes the staged test package; it does not touch Fire Launcher.
set -u

SERIAL="${SERIAL:-}"
[ -n "$SERIAL" ] || { echo 'Set SERIAL to the recorded device serial.' >&2; exit 2; }

adb -s "$SERIAL" uninstall juniojsv.mtk.easy.su
