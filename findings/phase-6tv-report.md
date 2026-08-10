# Phase 6TV host-only control-surface and test reconciliation

This bundle integrates Phase 6TO IPC sink audit, Phase 6TP OTA writer audit, Phase 6TQ GPL/exact-image driver inventory, Phase 6TR historical-test reconciliation, and the fresh Phase 6TU read-only device summary. It preserves the caller → gate → identity/user scope → exact sink acceptance rule.

Generation HEAD: `2ad6b19805b4db6f9563e6429b4067ccfe02fa33`.

## Safety boundary

No Binder/service call, driver `open/ioctl`, proc/sysfs/debugfs write, OTA construction or execution, recovery/sideload/flash, Root/exploit, reboot, package/settings mutation, Fire Launcher mutation, or partition write was performed. Phase 6TU used only read-only ADB queries with the specified device serial; raw settings remain local.

## Inputs

- **6TO IPC sink audit:** `work/luna_worker_phase6to_ipc_sink_audit_20260810.md` (2e7d1e0b8c091e8c69573abf136368fae3b700407ba3c074d1b2c513228148a6); `work/luna_worker_phase6to_ipc_sink_audit_20260810.csv` (43b7c270de32105680b12969b1a8dbd5a84d37a82a06d5ae24d08d0185e469a5); 15 row(s).
- **6TP OTA writer audit:** `work/luna_worker_phase6tp_ota_writer_audit_20260810.md` (1f2b859aa5113cd9c51fa325314017929910a8400458256119326c6cbcbdf7b5); `work/luna_worker_phase6tp_ota_writer_audit_20260810.csv` (949dd5515b55d0e4061c495156bc983f7c55a7193a33cabaa2d558b642d32440); 12 row(s).
- **6TQ driver inventory:** `work/luna_worker_phase6tq_driver_inventory_20260810.md` (d6cd5da0ff28632e1bca65f0e7c0255b4f6783b717a86a7a8662df1d93edba43); `work/luna_worker_phase6tq_driver_inventory_20260810.csv` (289dde4546aacc33aaacec0f715d2f5dbd2ddcd0cde9f415f90c7ac14c0567b5); 24 row(s).
- **6TR test reconciliation:** `work/luna_worker_phase6tr_test_reconciliation_20260810.md` (1d1c267a88bb3d2e96f1a5e0d0d7d46368f136c81f591c6a6b17964b5b7a4b30); `work/luna_worker_phase6tr_test_reconciliation_20260810.csv` (04c49baf1fd96f32a5497022d43486b6651f4f1a0656c46ab52f4786cf728cd3); 25 row(s).

Context hashes: `findings/phase-6tm-report.md` (73ea2ed41c91f96958172fe3b5e034e75324ebbd249341a6db37e74bffc48d89); `findings/phase-6tm-evidence-index.md` (90917fa9eace7d49435cd1114cbda1b34fdd7950967db77b85941e8ef06aac56); `output/tables/phase6tm-control-surface.csv` (e207284a5701448da27ac5fa0dbf844190e94c534876a0540e92a16affdd1444); `findings/phase-6tu-readonly-snapshot.md` (e83a3529a63a05c5a1fa1f2c86c18eed764d8027f444dcd2eed10b7e8ae0fae0); `output/tables/phase6tu-readonly-state.csv` (83cb7258da8177858bfd827a2cdda0dfaf0b960dd9ab2785b7800ec023b3dee2)

## IPC result

The bounded exact-build corpus found no confirmed chain from an ordinary app/shell caller through an accepted permission/identity gate to a User-0 HOME or Fire package-state sink. Amazon Activity/DevicePolicy/Window/Package services show scoped permissions, callbacks, metadata or policy effects. The AmazonUserManager KFT setter is child/profile-scoped in the available evidence. Exported components and signature declarations are not treated as bugs.

## OTA result

The saved updater script and native analysis show privileged target/write capabilities and cache helpers, but caller authentication, complete canonicalization/symlink data flow and runtime recovery reachability remain `UNKNOWN`. No payload or bypass is produced.

## Driver result

GPL source and exact-image metadata close selected read-only Amazon proc nodes, policy labels and several MediaTek registration surfaces. ION, M4U, MDP, TCPC, input, RPMB, debugfs and `amzn_drv_test` retain missing shipped/caller/policy/effect edges. No driver surface reaches PackageManager, ActivityManager, HOME or Fire Launcher in this corpus.

## Existing-test result

The reconciliation matrix records 25 historical rows. Priority APK, ordinary set-home, Fire package/component mutation, child/KFT/private Binder, accessibility replay, driver ioctl, OTA/recovery and root/partition routes are marked duplicate, closed, refused or not safe to replay. Historical rollback guards are evidence for those runs only.

## Current read-only state

The Phase 6TU redacted summary records PS7331.4463N / KFTRWI / trona, Android 9/API 28, security patch 2024-08-01, SELinux Enforcing, verified boot green, two users, and HOME resolver result `com.amazon.firelauncher/.Launcher` with effective priority 50. This is a current read-only observation, not a new workaround or privilege result.

## Verdict

No new safe evidence justifies a Root claim, Fire Launcher disablement, a shell-to-system confused-deputy claim, an OTA bypass, or a driver exploit. Remaining `UNKNOWN` rows are research gaps, not proof of absence.

Integrated rows: `76`; parse warnings: `0`.

Warnings:
- None detected.
