# Phase 6UM — broad privilege-surface and reachability closure

This host-only bundle broadens the analysis beyond Launcher to Amazon Framework IPC, the exact PS7331 OTA/update boundary, GPL/native driver capability, and prior-test reconciliation. It keeps the required security chain explicit: caller → permission/service-manager gate → identity/user scope → exact sink → observed effect.

Generation HEAD: `ef55e291118b567e45eaf7783db6c3962a714a01`.

## Safety boundary

No Binder transaction, service call, driver open/ioctl, malformed OTA, updater/recovery execution, package/settings mutation, user provisioning, reboot, Root/exploit attempt, Fire Launcher mutation, or partition write was performed. The device contribution is a serial-bound read-only snapshot; raw settings/service dumps remain local.

## Inputs

- **6UI IPC privileged sinks:** `work/luna_worker_phase6ui_ipc_sinks_20260810.md` (29d374ae81f2a30733dd25bab7f8ba955e2b3aeb7c9d24ce35d75140d85eeaaf); `work/luna_worker_phase6ui_ipc_sinks_20260810.csv` (5dc944d2f618ede728cf83de0d8c9f00af9f9aad51c32d596936c2e7a7deed82); 12 row(s).
- **6UJ OTA post-install:** `work/luna_worker_phase6uj_ota_postinstall_20260810.md` (3446ecd40b4ff65decd2b958deb5f369ab16981ab33fe05f08168b5711c3e257); `work/luna_worker_phase6uj_ota_postinstall_20260810.csv` (437c6aeb639b38fb1203261d75d129d3b4047376b2396c3bf0e7f1c82cbb568e); 21 row(s).
- **6UK GPL driver surface:** `work/luna_worker_phase6uk_driver_surface_20260810.md` (8117fe52ca293d5886e9a2f76eae4344068b5c0ae20e1860a7f43b28a47d9950); `work/luna_worker_phase6uk_driver_surface_20260810.csv` (021d5d2ef514959202e19867ccec9784b9bb302e847c66c1bc6103bb4538a6f2); 11 row(s).
- **6UL historical test reconciliation:** `work/luna_worker_phase6ul_test_reconciliation_20260810.md` (1c7372db02db19ca7c74b0b7e181dd83544c51c948b9793ab2533e2fd42846c3); `work/luna_worker_phase6ul_test_reconciliation_20260810.csv` (6de2b11fc924413e4a33cdcfdba99353785f1f66826d875db3fe46bc4b36416b); 21 row(s).

Context hashes: `findings/phase-6uh-report.md` (d6016b894566d40e26d043efa43df1e8ba313c9ba23d9b3d976f29a59734adc2); `output/tables/phase6uh-control-surface.csv` (ba473497b8c7a0fbef6a77951db183798c474a911b2a60b5cca510de53aeabec); `findings/phase-6py-service-state-exported-closure.md` (6f1a7a07e38eb92f4c65511ee3533b7809ce31c3db9bf76677c4c2d7d86d1898); `output/tables/phase6py-service-state-exported-closure.csv` (cf26ff1c72c0a6eefaa66aa26ce7675ec24b452f8e8844c347b3be358d358a6b); `findings/phase-6nj-followup-synthesis.md` (8c57ec3d603510c57704dd72ea0a115bc7f17b1b856946ee3091a450af01589c); `findings/phase-6ui-readonly-snapshot.md` (0983f132483e235d82b35a0b0f42f7dd577666249c3b347c891e8e35773b5882); `output/tables/phase6ui-readonly-state.csv` (7cfe1aa24ac4eeffca6147935ebac6ed9f71e92cde31b669eeead92e3ffcdc5b)

## Current device comparator

The fresh read-only capture identifies PS7331.4463N / KFTRWI / trona, Android 9/API 28, security patch 2024-08-01, verified boot `green`, SELinux `Enforcing`, two users, and HOME still resolving to `com.amazon.firelauncher/.Launcher` at effective priority 50. This is observation evidence only and does not imply that the visible service or any static sink is shell-reachable.

## Findings

### IPC and state sinks — **已證實 / bounded static**

The IPC inventory confirms concrete sinks: KFT tx3 can write Tahoe/Fire/Launcher3 state for supplied `UserInfo.id`; DPM/PMS persistent-preferred paths have active-admin/profile-owner and system-UID gates; PMS enabled-state and preferred-activity setters are real state sinks. Amazon activity/window/input/package services expose additional effects, but private-service handle reachability and method authorization remain separate requirements. No ordinary-app or shell → accepted identity → User-0 state/root path is closed.

### OTA and post-install — **已證實 capability / no bypass**

The exact local package is a signed release full block OTA for `trona`, with product/build gates, block verification symbols, recovery/update-binary dispatch, and direct partition/cache writers. `BootAfterSystemOTA` is a system-server phase-550 upgrade lifecycle path that resets setup/OOBE state; the reviewed chain has no ordinary preferred-HOME or Fire-state writer. Canonicalization, native recovery verification and AVB rollback details remain partially UNKNOWN. Static partition-writing capability is not an untrusted caller or safe workaround.

### GPL/native drivers — **已證實 capability / reachability UNKNOWN**

The exact source/config evidence contains CMDQ, ION/MTK ION, Amazon LD, debugfs/proc/sysfs and module capability surfaces. `CONFIG_DEVMEM`/`CONFIG_DEVKMEM` are disabled, while the selected config enables modules, CMDQ, ION and SELinux. Exact linked module/DTB provenance, device-node modes/labels, native retail caller, and runtime effect are not closed. No node was opened and no ioctl was issued.

### Existing tests — **已排除 within recorded conditions**

The reconciled ledger marks repeated HOME/priority/set-home tests, package/PMS setters, raw KFT/private Binder attempts, protected OOBE/OTA replay, driver access, provisioning and root/boot paths as duplicates, bounded negatives, or risk-rejected. A new filename does not create a new result when build, user topology and rollback state are unchanged.

## Broad conclusion

The project now has high-impact capability evidence across IPC, OTA and kernel-native layers, but the decisive low-privilege caller/authorization/user-scope/effect chain is still missing. Therefore no compliant evidence supports claiming root, a confused deputy, a Fire Launcher disable route, or a formal User-0 HOME replacement. The best remaining safe targets are artifact-completeness joins (module/DT/policy/client), not guessing Binder codes, crafting OTA input, or invoking driver interfaces.

## Verdict labels

- **已證實:** exact build/static sink or read-only device state within the preserved scope.
- **高可信推論:** capability or bounded control-flow interpretation with a named missing edge.
- **待驗證:** caller, permission, identity, user scope, loader or downstream effect is missing.
- **已排除:** the stated effect did not occur in the recorded test conditions.
- **因風險拒絕測試:** operation was not performed because it would cross the safety boundary.

Integrated rows: `65`; parse warnings: `0`.

Warnings:
- None detected.
