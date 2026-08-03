# Phase 4 risk register

| Risk / operation | Decision | Reason | Recovery |
|---|---|---|---|
| disable/hide/suspend/uninstall/force-stop/clear Fire Launcher | 因風險拒絕測試 | explicit Phase 4 safety boundary; may remove the only usable HOME | not applicable; never executed |
| Device Owner / managed provisioning | 因風險拒絕測試 | may require factory reset to remove | no safe no-reset guarantee |
| core SystemUI/Settings/overlay mutation | 因風險拒絕測試 unless exact reversible target | may remove navigation/settings access | only static/read-only analysis |
| unknown Binder transaction | 因風險拒絕測試 | no verified descriptor/permission/rollback | none |
| controlled test APK install/remove | 允許 | non-core package, explicit serial, uninstall rollback | `pm uninstall --user 0 TEST_PACKAGE` |
| ordinary preferred write for a new test package | avoid repeat | Phase 3C already disproved it under unchanged conditions | restore saved Fire preferred record, uninstall test package |
| accessibility redirect | user-consent required | must be explicitly enabled by device owner; no auto-consent | disable service, uninstall APK |
| normal reboot | only after a proven safe mutation | must preserve baseline and wait for ADB/system ready | post-reboot snapshot and explicit rollback |
| deliberate HOME crash/fallback | 因風險拒絕測試 | could create no-HOME or crash loop | static analysis only |
