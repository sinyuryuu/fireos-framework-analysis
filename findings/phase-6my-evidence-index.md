# Phase 6MY evidence index

All entries are host-only and refer to immutable preserved inputs. No device
was contacted.

| Evidence ID | Source | Observation | Classification | Confidence |
|---|---|---|---|---|
| 6MY-E01 | `fosservices:96087-96126` | Phase 550 + `isUpgrade()` sends the post-OTA action with permission | guarded lifecycle sender | Confirmed |
| 6MY-E02 | `BootAfterSystemOTAReceiver.java:27-61` | Guarded branch calls OOBE enablement; catch disables only receiver | OOBE state path | Confirmed |
| 6MY-E03 | `PackageHelper.java:11-22` | Standard component-state API receives OOBE component and state 1/2 | component writer | Confirmed |
| 6MY-E04 | `OOBEActivationHelper.java:53-56`; `SettingsDBUtils.java:51-64` | OOBE setup keys are written through context ContentResolver | settings writer | Confirmed |
| 6MY-E05 | `boot-framework-dis:435176-435236,449092-449185,452137-452150` | Receiver context retains user scope into PM/provider calls | user mapping | Strong evidence |
| 6MY-E06 | bounded source scan | No Fire Launcher or ordinary preferred-HOME writer in reviewed chain | bounded negative | Confirmed within scope |
| 6MY-E07 | safety boundary | Manual broadcast/OTA replay can change setup and component state | rejected experiment |因風險拒絕測試|

Input/output integrity is recorded in `artifacts/phase6my-bootafter-ota-package-helper-20260810-01/sha256sums.txt`.
