#!/usr/bin/env bash
# Idempotent rollback for the stopped MTK-EASY-SU-ROOT-T01 test.
set -u
SERIAL="${SERIAL:-}"
[ -n "$SERIAL" ] || { echo 'Set SERIAL to the recorded device serial.' >&2; exit 2; }
adb -s "$SERIAL" uninstall juniojsv.mtk.easy.su
