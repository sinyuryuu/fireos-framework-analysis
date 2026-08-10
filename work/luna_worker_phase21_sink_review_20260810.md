# Phase 21E — cross-surface sink review

日期：2026-08-10。範圍限於 Phase 20 provenance ledger、exact PS7331 selected/compiled framework/services artifacts、保存的 native/artifact reports 與既有 sink ledgers。未接設備、未執行 Binder/ADB/OTA/ELF/exploit、未操作 driver、未改檔。本輪只新增本報告與同名 CSV。

## 結論

在本輪去重後，沒有發現一條新的、同時閉合 `caller → gate → identity/user scope → sink`，並且能落到以下任一目標的完整鏈：

- PackageManager enabled-state 或 HOME replacement；
- User 0 明確選擇/寫入；
- UID 0 或等價 privilege transition；
- partition write / boot-chain writer；
- kernel-memory / credential sink。

既有 corpus 仍有幾類「局部閉合」或「能力已證實但身份/入口未閉合」的路徑。它們在 P21E ledger 中保留為已證實、高可信或待驗證，但不升格成新的完整鏈，也不把 PS7331 artifact 套到 PS7330。

## Exact PS7331 input boundary

本輪以以下 exact PS7331 extraction manifests 作 artifact boundary：

- selected manifest：`firmware/extracted/PS7331/selected/manifest.sha256`，內容 hash `b098f85287a729d03cfac1ac6f767a3ba6a15ce8c65d7f9e581cbbed75448a74`。
- compiled manifest：`firmware/extracted/PS7331/compiled-02/manifest.sha256`，內容 hash `7da7040b4c7454084d8c30452edc05d4c68ce3813fe20700d4016036e4097716`。
- selected framework/services：`framework.jar`/`services.jar` 均 `1c16f5976318fadcf7add92c518a93896f99e2a78f742b7347d8539103264882`；`fosframework.jar` `ef1491b8850be6d6cab0101d6b4fcf34e1dabb13cd2d08e3d72e615ddb21d188`；`fosservices.jar` `364603c0228058973ed976ff1bef51c3cab2fa8fc163ec63c727157bb92dec96`。
- compiled PS7331 services/framework VDEX/ODEX hashes are recorded in P21E-002/P21E-003 below.

`artifacts/framework/*`、`artifacts/services/*` 的部分同名檔案是 2026-08-03 device-pulled PS7330-baseline capture；本輪不把那些 path 當作 PS7331 exact runtime input。JAR SHA 相同只表示 bytes 相同，不足以證明整套 framework/VDEX/ODEX、runtime 或 build 相同。

## Cross-surface findings

### 已證實

**P21E-001 — existing PMS enabled-state writer is static, not a new closed chain.**

Exact PS7331 compiled service evidence shows Amazon KFT lifecycle code invoking `setComponentEnabledSetting` / `setApplicationEnabledSetting` for the supplied `UserInfo.id`, including Fire Launcher/Launcher3-related state. This supports a PackageManager enabled-state sink at the static method boundary. The saved ledger already records the same sink; no new caller identity, inherited permission gate, or proof that `UserInfo.id == User 0` was found. Therefore this is a confirmed static sink, not a new complete caller-to-User-0 chain.

Evidence: exact PS7331 selected/compiled manifests above; `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` enabled-setting call sites; `work/luna_worker_phase20_ipc_closure_20260810.md`; `output/tables/phase19-caller-gate-sink.csv`.

**P21E-002 — PS7331 compiled framework/services artifacts are present, but no additional HOME writer was closed.**

The exact compiled artifacts are:

- `services.vdex` `b3cdefcb8e150c478983195657a4ebaeb02ae9b9139756e09737361992b3f297`;
- `services.odex` `a4cee1acdaae7fcee905697979c4f9299bcc884bb1bcf55a5ee9f4034dc8f8d2`;
- `fosservices.vdex` `e20411372ebfa1b8ec605d2903e8894392be1333d71746a659818b06876d8c1a`;
- `fosservices.odex` `8f8959b335a384af020e80cafffd622cbfed2a0d2cffc713e86077b97a092f0a`;
- `boot-framework.vdex` `992324d14a6e8c439dfa9578bbf0cd94ca7038c9cf3e5388d399334373958642`;
- `boot-fosframework.vdex` `00f7a0e1a77b9059051df6c8b3c88a5318a741b0c7cf3873fe9bfbb382a1e4dd`.

Their presence supports static inspection scope only. The existing HOME evidence remains the saved resolver/runtime result; no new PS7331-only caller→gate→User 0 HOME writer was recovered.

### 高可信但未形成新完整鏈

**P21E-003 — OTA partition writer capability remains privileged/static.**

PS7331 OTA `update-binary`/`updater-script` and existing native call-edge reports support fixed block-image, package extraction and boot-chain target capability. The missing recovery/native executor identity, AVB/rollback authority, SELinux/UID handoff and acceptance result remain open. This is not a new chain and does not prove partition write occurred on PS7330 or any device.

Evidence: `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` SHA `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5`; `work/luna_worker_phase20_provenance_20260810.md`; `work/luna_worker_phase20_ota_closure_20260810.md`; `output/tables/phase19-caller-gate-sink.csv`.

**P21E-004 — shipped native diagnostic/RPMB partial chains do not reach the requested package/HOME/kernel-memory sinks.**

Existing native joins connect `meta_tst` to gsensor/USB sysfs policy and `rpmb_svc` to RPMB device/policy. The latter has a strong init/domain indication but still lacks final object/DTB, complete callsite-to-device proof and TEE validation. These sinks are sensor/USB/persistent-storage state, not PackageManager, HOME, partition, kernel-memory or a demonstrated UID0 transition. No new cross-surface bridge was found.

Evidence: `work/luna_worker_phase20_driver_closure_20260810.md/.csv`; `artifacts/phase9/ps7331-runtime-binary-audit-20260806-01/vendor-bin/bin/{meta_tst,rpmb_svc}`; saved init/file-context/CIL reports.

### 待驗證

**P21E-005 — PackageManager callback fan-out has sink-shaped calls but lacks external caller and gate closure.**

The exact service disassembly contains callback paths referencing PackageManager operations such as `deletePackageX`, `removePackageLI`, `getPackagesForUid`, and enabled-setting calls. Existing reports cover the KFT enabled-state path; the remaining callback-shaped references do not establish a new ordinary caller, method-local authorization, accepted identity, target user, or enabled-state/HOME effect. A callback registration or a direct PMS method reference is not itself a complete chain.

Evidence: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log`; `work/luna_worker_phase20_ipc_closure_20260810.md`; `work/luna_worker_phase20_reconciliation_20260810.md`; `output/tables/phase19-caller-gate-sink.csv`.

**P21E-006 — current-user UI launch is not a HOME replacement chain.**

`AmazonProfileService.startProfilePicker` / related `startActivityAsUser` references show a current-user UI launch capability, but the bounded path has no preferred-activity/HOME setter, no explicit external caller identity closure, and no proof the configured component is the HOME resolver. It remains a UI-launch residual, not a new HOME/User-0 sink.

Evidence: existing Profile service method evidence and `work/luna_worker_phase20_ipc_closure_20260810.md`.

**P21E-007 — kernel/driver capability remains disconnected from a complete privilege sink.**

PS7331 Image/config/source and native driver ledgers retain CMDQ, M4U, uinput, ION, AUXADC, performance and liquid-detection candidates. Exact shipped opener/control-flow, selected DTB/object, effective UID/domain and downstream kernel-memory/credential effect are not jointly closed. `meta_tst`/`rpmb_svc` partials do not bridge this gap.

Evidence: `work/luna_worker_phase20_driver_closure_20260810.md/.csv`; `work/luna_worker_phase20_reconciliation_20260810.md`; PS7331 Image SHA from Phase 20 provenance.

### 風險拒絕

**P21E-008 — runtime or exploit confirmation rejected by scope.**

No Binder transaction, service call, broadcast, package/settings mutation, HOME replay, driver node open/ioctl, OTA/recovery/updater execution, partition write, kernel-memory operation, root payload or device contact was performed. These are not negative runtime results; they are explicitly out of scope and remain unverified.

## Final disposition

The only direct requested sink confirmed in the exact PS7331 service corpus is the already-known PackageManager enabled-state method boundary for KFT-related component/application state. Its trusted caller, authorization, accepted user and User-0 relation remain unresolved. No new complete caller→gate→identity→sink chain to HOME, User 0, UID 0, partition or kernel memory was found. PS7331 artifacts are not used to infer PS7330 runtime behavior.

