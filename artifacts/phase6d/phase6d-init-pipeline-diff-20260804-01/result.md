# Phase 6D /init pipeline differential

Host-only structural comparison. The stripped PS7331 `/init` was not executed, no SELinux policy was loaded, and no device state was changed.

## Results

- **已證實：** official AOSP Android 9 source contains the expected SELinux loader anchors; the selected r1/r61 `selinux.cpp` files have the same SHA-256.
- **已證實：** the PS7331 `/init` evidence contains code-level references to standard and `rootable_*` policy paths and a common stripped helper candidate.
- **高可信推論：** the binary contains a policy-selection/loading decision surface structurally related to the AOSP split-policy pipeline.
- **待驗證：** exact symbol mapping, branch predicate, caller of the property parser, and the policy variant active on the stock boot.
- **無法取得證據：** the GPL archive does not include `system/core/init`; therefore it cannot supply an Amazon-vs-AOSP source diff for `/init`.
- **因風險拒絕測試：** boot-property injection, alternate policy loading, remount, bootloader/fastboot, image writes, kernel race/panic, and root payloads.

See `pipeline.json`, `anchor-map.csv`, and `pipeline-knowledge-base.mmd` for machine-readable evidence and the conservative mapping.
