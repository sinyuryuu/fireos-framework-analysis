#!/usr/bin/env bash
# Exact rollback for PM-UNINSTALL-FIRE-T01. Run only with the recorded device.
set -u
: "${SERIAL:?Set SERIAL to G001LT0511550CFT before restoring}"
adb -s "$SERIAL" shell pm install-existing --user 0 com.amazon.firelauncher
adb -s "$SERIAL" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME --user 0
adb -s "$SERIAL" shell dumpsys package com.amazon.firelauncher
