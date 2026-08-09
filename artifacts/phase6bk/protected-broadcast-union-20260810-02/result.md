# Phase 6AD：saved APK protected-broadcast inventory

- Explicit APK inputs: **45**
- Target action: `amazon.intent.action.BOOT_AFTER_SYSTEM_OTA`
- Target declarations in scanned scope: **1**
- AAPT failures: **0**
- Classification: **CONFIRMED_IN_SCANNED_SOURCES**

This is host-only provenance analysis over the explicitly supplied preserved APKs.
It does not prove the complete runtime `PackageManagerService.mProtectedBroadcasts`
set and does not make manual broadcast delivery safe.

No ADB, broadcast, Binder transaction, OTA/recovery operation, package/settings
mutation, reboot, or partition write was performed.
