# Phase 3C risk register

| Operation | Decision | Rollback or reason |
|---|---|---|
| Ordinary preferred HOME write | Executed once | set Fire preferred |
| Test APK install/remove | Executed once | uninstall p0 exit 0 |
| Settings mutation | Not executed | no exact HOME reader/writer |
| HOME role set | Not executed | role API output unavailable |
| device_config mutation | Not executed | command unavailable |
| Core overlay switch | Rejected | SystemUI/navigation risk |
| Fire package state/data | Prohibited | project safety boundary |
| Device Owner/provisioning | Rejected | possible reset requirement |
| Crash/fallback APK | Deferred | recovery-first APK required |
| Reboot | Executed once | ADB returned and state was captured |

No stop condition was triggered. Final ADB state was device and Fire HOME was
resolved.
