#!/usr/bin/env bash
set -u
: "${SERIAL:?Set SERIAL to G001LT0511550CFT before running restore}"
adb -s "$SERIAL" shell pm unhide --user 0 com.amazon.firelauncher
