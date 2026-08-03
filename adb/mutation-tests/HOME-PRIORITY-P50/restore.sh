#!/usr/bin/env bash
set -u
adb -s 'G001LT0511550CFT' shell cmd package clear-package-preferred-activities 'org.fireosresearch.home.p50'
adb -s 'G001LT0511550CFT' shell cmd package set-home-activity 'com.amazon.firelauncher/com.amazon.firelauncher.Launcher'
adb -s 'G001LT0511550CFT' uninstall 'org.fireosresearch.home.p50'
