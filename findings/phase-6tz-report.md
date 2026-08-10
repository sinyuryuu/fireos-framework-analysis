# Phase 6TZ host-only permission, writer and driver closure

This bundle integrates the H2 custom-permission owner/grant search, the User-0 Fire restoration-writer provenance search, and the exact-build `amzn_drv_test` closure. It preserves the requirement for caller → gate → identity/user scope → exact sink.

Generation HEAD: `654b01040847e82253c8b6ba54951d82f4fcc361`.

## Safety boundary

No device, adb, Binder bind/call, service call, broadcast, driver open/ioctl, proc/sysfs/debugfs write, Root/exploit, OTA/recovery/flash, reboot, package/settings mutation, or partition write was performed.

## Inputs

- **6TW H2 owner/grant:** `work/luna_worker_phase6tw_h2_owner_grant_20260810.md` (19abc44591dd66e1cbc5ab076fa3043c75dbf6da018d6e30022f78f3469d0f11); `work/luna_worker_phase6tw_h2_owner_grant_20260810.csv` (44187e7f8a4325a19a5802894de6b21ab2e228b01d1b60b9ccf55ad4d35e53fb); 16 row(s).
- **6TX amzn_drv_test closure:** `work/luna_worker_phase6tx_amzn_drv_test_closure_20260810.md` (78223086a6d90c2313e350f2effb1f4ac4c0ce435b5b3521e649f83df3c9dfeb); `work/luna_worker_phase6tx_amzn_drv_test_closure_20260810.csv` (6c48832be2d2e7553787edb1539e4760f8f0b79c769d76571528c6b4ca091649); 14 row(s).
- **6TY User-0 Fire writer:** `work/luna_worker_phase6ty_user0_fire_restoration_20260810.md` (7d536a8bae7e605a4ca1002e891448a199b4b8970677ae751dbfbb41e4eca4ab); `work/luna_worker_phase6ty_user0_fire_restoration_20260810.csv` (92c63e2f2896e6c703ba04868f249f0115441df90ea5491164cbcfe7d24e9fb5); 10 row(s).

Context hashes: `findings/phase-6tv-report.md` (e766794a9683923e11a723e11d4e1b772512212745699f8e071e5ac0bb4cd31f); `findings/phase-6tv-evidence-index.md` (bdda99c2d5902704262b9c0e7510fe6ac01c1ba217dcff019a04cc7cb343cb77); `output/tables/phase6tv-control-surface.csv` (06d9ab983c087a10491a97629bab997a7bbb5fde29974c01b250f192a880b507); `findings/phase-6tu-readonly-snapshot.md` (e83a3529a63a05c5a1fa1f2c86c18eed764d8027f444dcd2eed10b7e8ae0fae0)

## H2 owner/grant result

The exact PackageManager permission record identifies `android.amazon.perm` as the owner of `com.amazon.alta.h2clientservice.permission.BIND_SERVICE`, UID 1000, with `signature|amazon` protection. Ten exact custom grant records identify candidate packages, but their manifest `uses-permission` requests, code-level bind edges and accepted runtime caller identities remain `UNKNOWN`. This is positive permission provenance, not a confused-deputy or shell-reachability finding.

## User-0 Fire writer result

The child/KFT writer explicitly targets `com.amazon.firelauncher` with `UserInfo.id`, but the available evidence is child/profile scoped and does not prove User 0. Fixed OOBE and generic ProductPolicy setters are separate non-Fire/HOME writers. No exact production caller → gate → User-0 Fire restoration setter or preferred-HOME write was closed.

## amzn_drv_test result

Source Kconfig/Makefile registration is present, but the exact final PS7331 config does not select `CONFIG_AMZN_DRV_TEST`, unique Image markers are absent, and the audited module/manifest corpus has no matching payload. Runtime `/proc/amzn_drvs` nodes, labels, init/uevent load and caller/effect remain `UNKNOWN`; no source registration is promoted to a shipped exploit surface.

## Overall verdict

This round improves provenance but still provides no safe basis for invoking private Binder, writing a driver node, changing Fire Launcher state, or claiming Root. The strongest new fact is the UID-1000 custom permission owner and its ten explicit grants; the missing request/bind/sink join is the next host-only evidence target.

Integrated rows: `40`; parse warnings: `0`.

Warnings:
- None detected.
