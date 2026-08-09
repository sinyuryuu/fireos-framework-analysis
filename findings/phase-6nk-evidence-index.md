# Phase 6NK evidence index

| Evidence ID | Source | SHA-256 | Observation | Confidence |
|---|---|---|---|---|
| 6NK-IPC-001 | `work/luna_worker_phase6_ipc_kft_audit_20260810.md`; `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:54297-54325` | `93d6b39f721b1bd1e31f1d0423336f21343f8bca537147b437196827e3852755`; VDEX `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | KFT writer targets Tahoe, Fire Launcher and Launcher3 using supplied `UserInfo.id`. | Confirmed |
| 6NK-IPC-002 | `boot-fosframework/disassembly.log:370378-370750`; `fosservices/disassembly.log:54415-54478` | VDEX `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`; `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` | tx3 interface/Stub mapping is present; complete inherited authorization remains unresolved. | Confirmed contract / Unknown authorization |
| 6NK-IPC-003 | Existing `adb/phase6fj/`, `adb/phase6fk/`, `adb/phase6cz/` captures | Hashes recorded in their manifests | Ordinary tx3 callers hit downstream cross-user/PMS gates; shell private-service lookup is denied. | Confirmed |
| 6NK-IPC-004 | `work/luna_worker_phase6_ipc_kft_audit_20260810.md` | `1bebc7838cc9000a26f469bde50879160f785c44369976e6ed3cab11d93df60f` | Reviewed Amazon PM tx1–tx11 contract has no formal HOME/preferred/package-state setter. | Confirmed, bounded |
| 6NK-POL-001 | `findings/phase-6ce-product-policy-firelauncher-boundary.md`; `adb/phase6ce/product-policy-firelauncher-boundary-20260805-03/` | Report `54a4248153a41824665f3a8432b6586940b45a03b955518e19b77e5333a35dd0`; capture manifest in directory | PS7331 Product Policy inputs contain no `com.amazon.firelauncher`; service is local/trusted. | Confirmed |
| 6NK-OTA-001 | `work/luna_worker_phase6_ota_postinstall_audit_20260810.md` | `7ee15036830b408152856c84dea8bd24050a8ff6a102de40383413e3d83f7629` | OTA/recovery writer capability is separated from ordinary shell/APK reachability. | Strong evidence |
| 6NK-OTA-002 | Existing `adb/phase6ae/`, `adb/phase6bk/` captures | Hashes recorded in their manifests | `otadexopt` adjacent shell path is not evidence of partition/HOME/root writer. | Confirmed, bounded |
| 6NK-SRC-001 | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2`; `findings/phase-6an-gpl-scope.md` | Source archive `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`; report hash in source report | Released GPL corpus lacks Android userspace `system/core/init` and `selinux.cpp`. | Confirmed |
| 6NK-LAUNCH-001 | `work/luna_worker_phase6_launcher_options_20260810.md`; `findings/home-priority-experiment.md` | `b4bef7a2b56d7378e0b293ff91b2db9c6f964a7fd4342189770492dd317fcad0` | Priority, ordinary preferred, child/profile, OOBE and Lock Task results are separated by scope. | Confirmed, existing evidence |
| 6NK-LAUNCH-002 | `findings/phase-6hb-ms-accessibility-reboot-persistence.md` | Hash recorded in report/artifact manifest | Accessibility foreground fallback is practical but does not change formal HOME. | Confirmed / Strong evidence |

## Safety fields

- `device_contacted_for_new_tests`: false
- `binder_transaction_sent`: false
- `unknown_transaction_sent`: false
- `ota_or_recovery_executed`: false
- `ioctl_or_device_node_access`: false
- `fire_launcher_state_mutated`: false
- `root_or_privilege_escalation_attempted`: false
- `credentials_used_or_stored`: false
