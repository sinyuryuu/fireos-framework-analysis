# Phase 6AW evidence index

| Evidence ID | Source | File / method | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| 6AW-OTA-001 | PS7331 OTA | `META-INF/com/android/metadata`, `ota.prop` | Device/build/security-patch/full-package metadata match `trona` / PS7331 | Provenance and compatibility boundary | Confirmed |
| 6AW-OTA-002 | PS7331 OTA | `META-INF/com/google/android/updater-script:6,10` | Date and device guards are evaluated before update operations | Lifecycle gate, not a launcher setting | Confirmed |
| 6AW-OTA-003 | PS7331 OTA | `updater-script:6-24` | `block_image_update` and direct boot/firmware extraction targets are present | Package has high-impact write intent | Confirmed (static) |
| 6AW-OTA-004 | Saved native analysis | `artifacts/phase6ah/update-binary-validation-20260805-01/analysis.json` | Registration, evaluation, block-image, verification and I/O edges are preserved | Host-side implementation boundary | Confirmed (static) |
| 6AW-OTA-005 | Safety disposition | `artifacts/phase6aw/ota-write-contract-20260805-02/summary.json` | updater/recovery/partition_written all false | No device mutation occurred | Confirmed |
