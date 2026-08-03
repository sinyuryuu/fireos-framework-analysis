# Read-only ADB Command Plan

All commands below require an explicit serial and are intended for the baseline script. They do not change package state, settings, boot state or filesystem mounts.

| Command family | Hypothesis under test |
|---|---|
| `adb -s SERIAL shell getprop` | Exact model, build, API, Fire OS and security state |
| `adb -s SERIAL shell pm list packages ...` | Package inventory and enabled/disabled candidates |
| `adb -s SERIAL shell cmd package resolve-activity ... HOME` | Standard HOME resolver result |
| `adb -s SERIAL shell cmd package query-activities ... HOME` | All HOME candidates and priorities |
| `adb -s SERIAL shell dumpsys package preferred-activities` | Preferred versus persistent preferred activities |
| `adb -s SERIAL shell dumpsys package PACKAGE` | Package flags, UID, permissions, persistence and filters |
| `adb -s SERIAL shell service list`, `dumpsys -l`, `ps` | Amazon activity/window/input/package services |
| `adb -s SERIAL shell dumpsys activity/window/input` | Current foreground and input state |
| `adb -s SERIAL shell mount`, `getenforce`, `id`, `uname` | Mount and shell/security constraints |
| `adb -s SERIAL shell cmd overlay list` | Resource overlay involvement |
| `adb -s SERIAL shell settings list ...`, `device_config list` | Read-only configuration evidence |

Unsupported commands are retained with their stderr and exit status; the script uses the specified fallback resolver commands where available.

## Captured baseline status

Run `BASELINE-20260803-02` completed with all required commands successful. The recorded non-zero statuses were:

- `pm help`, `cmd package help`, and `cmd activity help`: exit 255 although help text was captured.
- `device_config list`: exit 127 because `/system/bin/sh` has no `device_config` binary.

These are environment/tool-support observations, not package-state failures. The complete command and status record is in `adb/baseline/BASELINE-20260803-02/command_manifest.tsv`.
