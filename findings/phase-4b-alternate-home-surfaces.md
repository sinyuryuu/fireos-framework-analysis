# Phase 4B — alternate HOME surfaces

## Static/read-only result

Android 9 contains the normal HOME start path (`startHomeActivityLocked()` and
`startHomeOnAllDisplays()` in the ActivityManager side), while the selected
Fire artifacts expose Amazon callback boundaries around resolution and Home
key policy. The repository's prior role/device_config probe found no usable
HOME role holder or device_config command on this build (`P3C-ROLE-001`).

No evidence in the selected Fire OS artifacts shows a user-level alternate
HOME that would replace the main HOME resolver without Device Owner, managed
profile policy, system UID, or a privileged package.

`CATEGORY_SECONDARY_HOME`, display-specific HOME, dock/car HOME, dream exit,
and lock-task/kiosk are **待驗證** only where the local artifact lacks a full
class/method implementation. Creating Device Owner or provisioning a managed
profile is **因風險拒絕測試** because reversal can require a factory reset.

No alternate HOME APK was installed in this phase; the Phase 4 alias APK is a
candidate-composition control and is not advertised as a secondary HOME.
