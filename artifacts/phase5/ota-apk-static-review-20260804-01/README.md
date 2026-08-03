# OTA APK static review

## Inputs

This directory documents the offline review of the existing Phase 3B OTA APK artifacts. No APK was executed on the device and no OTA install path was called.

| File | SHA-256 |
|---|---|
| artifacts/phase3b-ota/com.amazon.device.software.ota__0_DeviceSoftwareOTA.apk | 4a00b81fda6259e1309d9c6c3021e7d958be8bc6341a49b1278216580824b2a0 |
| artifacts/phase3b-ota/com.amazon.device.software.ota.override__0_DeviceSoftwareOTAIdleOverride.apk | b0d78110e5f1b58efc7c741936fcc2233c05a06ea5bd65f4cf2237c3e3c1118b |

Tool: JADX 1.5.6.

## Static observations

The DeviceSoftwareOTA APK contains the following relevant data-model and control-flow names:

- DBHelper and updates.db
- PublishedUpdates.RemoteURI
- PendingUpdates.LocalURI
- OTADataDirectory with /data/ota_package/ preference when available
- SideloadDirectory for external-storage scanning
- OTABootReceiver for boot-time OTA scheduling
- UpdateSystemWrapper.install() calling UpdateSystem.install()

These observations identify where an OTA package URI could be represented. They do not show the contents of the current device database.

The live shell capture could not enumerate the OTA application private data directory. No permission bypass was attempted.

## Classification

- **已證實：** the APK contains the above schema and storage code names.
- **高可信推論：** a completed or pending OTA may be represented by database or local-storage records that are not visible to shell.
- **無法取得證據：** the actual PS7330 RemoteURI, LocalURI or pending record on this device.
- **因風險拒絕測試：** no UpdateSystem install, private Binder call, permission bypass, or OTA check/download trigger.

See findings/phase-5au-ota-residue-review.md and findings/phase-5au-evidence-index.md for the device-scoped conclusions.
