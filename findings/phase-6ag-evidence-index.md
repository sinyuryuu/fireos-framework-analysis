# Phase 6AG evidence index：BootAfterSystemOTAReceiver research item

本索引只登錄既有證據，不宣稱 Phase 6AG 重新執行裝置測試。

## E6AG-01 — guarded system-server sender

- **Source:** Fire OS services VDEX
- **File:** `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:96107-96126`
- **SHA-256:** `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- **Test ID:** `PHASE6Q-HOST-OOBE-20260805-01`
- **Observed result:** phase `550` and `PackageManagerService.isUpgrade()` gate the action sender.
- **Interpretation:** arbitrary action replay is not equivalent to the verified sender lifecycle.
- **Confidence:** Confirmed

## E6AG-02 — receiver side effects

- **Source:** OOBE JADX output
- **File:** `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/BootAfterSystemOTAReceiver.java:22,27-80`
- **SHA-256:** `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90`
- **Test ID:** `PHASE6Q-HOST-OOBE-20260805-01`
- **Observed result:** guarded incremental flow enables `OobeHomeActivity` and calls `OOBEActivationHelper.activateOOBEIF()`; catch path can disable the receiver.
- **Interpretation:** this is setup/OOBE state mutation, not a generic HOME API.
- **Confidence:** Confirmed static

## E6AG-03 — source-package protected broadcast

- **Source:** device-pulled `android.amazon.perm.apk` plus package dump
- **File:** `artifacts/phase6ac/android-amazon-perm-device-20260805-01/android.amazon.perm.apk`; `adb/phase6ac/PHASE6AC-RO-20260805-01/`
- **SHA-256:** `5b72bdfcfb91b28d2c751e548f60d406de5c3cbb235e47e232014abdebcdc058`
- **Test ID:** `PHASE6AC-RO-20260805-01`
- **Observed result:** manifest contains `amazon.intent.action.BOOT_AFTER_SYSTEM_OTA` as `protected-broadcast`; package dump gives `signature|amazon`, source `android.amazon.perm`, UID 1000.
- **Interpretation:** shell delivery is not established and is not assumed.
- **Confidence:** Confirmed bounded source result

## E6AG-04 — OOBE Home baseline

- **Source:** saved package dump
- **File:** `adb/phase6q/PHASE6Q-RO-20260805-01/oobe_package_dump.stdout.txt:30-36,415-424`
- **Test ID:** `PHASE6Q-RO-20260805-01`
- **Observed result:** `OobeHomeActivity` is a priority-100 HOME candidate but is disabled for User 0 in the saved baseline.
- **Interpretation:** static priority does not make the component an active daily HOME resolver result.
- **Confidence:** Confirmed

## E6AG-05 — setup-state mutation helper

- **Source:** OOBE JADX output
- **File:** `artifacts/phase6j/ota-oobe-ps7331-jadx-20260805-01/sources/com/amazon/kindle/otter/oobe/OOBEActivationHelper.java:53-56`
- **SHA-256:** `6ebcb7eef7a03459a76b9c21cd59b61a30947f2b00a5624a4646825b8e3223d2`
- **Observed result:** incremental activation writes `user_setup_complete=0` and `isOOBEActive=1`.
- **Interpretation:** actively testing the receiver risks entering OOBE and is rejected.
- **Confidence:** Confirmed static

## E6AG-06 — bounded APK inventory

- **Source:** Phase 6AD selected manifest inventory
- **File:** `artifacts/phase6ad/protected-broadcast-inventory-20260805-01/summary.json`; `output/tables/phase6ad-protected-broadcast-inventory.csv`
- **Observed result:** 28 selected manifests parsed; only `android.amazon.perm.apk` contained the target action.
- **Interpretation:** source duplication was not seen in the bounded scope; complete runtime membership remains open.
- **Confidence:** Strong evidence / bounded

## Safety disposition

No Phase 6AG broadcast, Binder transaction, OOBE activation, settings/package
mutation, OTA/recovery action, reboot, Root, or partition write was performed.
