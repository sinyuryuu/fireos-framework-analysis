#!/usr/bin/env bash
set -u
adb -s 'G001LT0511550CFT' shell cmd package set-home-activity 'com.amazon.firelauncher/com.amazon.firelauncher.Launcher'
