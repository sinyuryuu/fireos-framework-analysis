#!/usr/bin/env bash
# Generated restore template. It is intentionally not executable by default.
# Fill in only commands corresponding to the mutation recorded in metadata.
# Verify the before/after snapshots before running any command.
set -u
: "${SERIAL:?Set SERIAL to the recorded device serial before restoring}"

# Examples for a preferred-home test (do not run unless that exact mutation
# was recorded in this test directory):
# adb -s "$SERIAL" shell cmd package set-home-activity com.amazon.firelauncher/.Launcher

# Examples for a settings key that was originally absent:
# adb -s "$SERIAL" shell settings delete global KEY

# Examples for a package state mutation:
# adb -s "$SERIAL" shell pm enable --user 0 PACKAGE

echo "Restore template only; no automatic restore command is defined."
