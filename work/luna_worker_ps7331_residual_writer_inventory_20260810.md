# PS7331 7.3.3.1 residual writer inventory

日期：2026-08-10。角色：Phase 6QB `luna_worker`。

## Scope and boundary

本輪只讀取工作區保存的 PS7331 7.3.3.1 source、boot/framework VDEX/JADX、fosinit、manifest、OTA 與既有 Phase 6 evidence。沒有接觸真機，沒有執行 Binder/service call、broadcast、ioctl、root/exploit、OTA、recovery、reboot、partition/write 或未知 transaction。未回退他人變更。

Phase 6PZ/6QA 已明確閉合、因此本檔不重列：`default_home`/`config_show_default_home`/Settings dashboard 與 overlay；普通 `set-home-activity`/priority 行為；`IAmazonPackageManager` tx6/tx7 ProxyReceiver；Vending `LauncherConfigurationReceiver`/`DseService`；以及 7.3.3.1 outer source tar EOF negative。已知 child-only KFT writer、protected Fire deny-list、ordinary priority/set-home 也排除，不把 privileged capability 當成可利用性。

## Result

以下 7 條是目前仍有研究價值的 bounded residual。每條均按 caller → permission/SELinux → identity → user scope → sink 分層；`UNKNOWN` 代表保存 corpus 尚未閉合，不代表漏洞或可由 shell/ordinary app 到達。

| ID | Residual / status | Exact evidence and sink | Safe next step |
|---|---|---|---|
| RWI-01 | `BOOT_AFTER_SYSTEM_OTA` sender：static confirmed；exact numeric delivered user unknown | `AmazonPackageManagerService.onBootPhase` `fosservices/disassembly.log:96087-96126`; system Context/user propagation `boot-framework-disassembly.log:449212-449262,449576-449604,452691-452721`；phase 550 + `isUpgrade()` + protected action；sink is AMS delivery to OOBE receiver | 只做保存 framework/Context user mapping 與自然授權 OTA 後的 read-only provenance；不 replay action |
| RWI-02 | OOBE component writer：sink confirmed；User-0/post-OTA timeline unknown；lifecycle-only | `BootAfterSystemOTAReceiver.java:27-61` → `PackageHelper.java:11-22`; enables `OobeHomeActivity` only under guarded OOBE branch；not Fire Launcher or formal third-party HOME setter | 自然官方 OTA 後只收集 read-only component/HOME state；不手動 enable |
| RWI-03 | OOBE settings writer：sink confirmed；exact context user unknown | `OOBEActivationHelper.java:53-56` → `SettingsDBUtils.java:51-64`; writes setup/OOBE Secure state, no preferred-HOME API | Host-only trace ContentResolver/PMS user handle；不寫 Settings |
| RWI-04 | Alexa system-OTA consumers：static lifecycle-only；receiver authorization/user scope incomplete | `SystemOTAReceiver.java` slices in `com.amazon.gemini.settings` and `com.amazon.alexa.multimodal.gemini`; secure/access-control settings sinks, no bounded Fire/HOME sink | Host-only manifest/source join；不送 protected action |
| RWI-05 | fosinit/runtime loader completeness：bounded corpus; runtime source set unknown | 123 XML corpus `artifacts/phase6jd-fosinit-20260808-01`; callback dispatch `services/disassembly.log:222435-222489`, AppCompat `fosservices/disassembly.log:41093-41147`; reviewed callbacks are resolver filtering/visibility, no preferred/package writer | Recover loader/class-loader source and compare all registrations offline；不做 system-server injection/Binder |
| RWI-06 | OTA verifier/staging → recovery/native updater：privileged capability confirmed; caller provenance/indirect dispatch unknown | Java verifier/staging evidence `findings/phase-6kt-recovery-verifier-provenance.md`; native path summary `artifacts/phase6md-native-updater-path-audit-20260810-02/summary.json`; sink capability includes extraction/block-image/partition write, but no shell/ordinary-app route | Offline verifier/certificate/AVB-to-recovery and registry/data-flow provenance；不執行 updater/recovery/crafted OTA |
| RWI-07 | updater canonicalization markers → write guard：markers confirmed; direct edge unknown | `update-binary` VA `0x1263ac/0x1263d9/0x126405/0x1312ea/0x1312f5`; `MakeFreeSpaceOnCache` `0x417778-0x417fc4`; registry `0x4069cc-0x407038`; selected graph has no direct canonicalization→write edge | Offline symbol-guided CFG/data-flow/error-path closure；不做 symlink/traversal、partition write、recovery 或 reboot |

## Interpretation

目前沒有一條已閉合的 `shell/ordinary app → accepted gate → system/root identity → User-0 Fire/package/HOME sink`。RWI-02/RWI-03 是受保護 OTA/OOBE lifecycle writer；RWI-06/RWI-07 是 recovery/update privileged capability；RWI-05 是 artifact completeness gap。它們都不能被宣稱為 exploit、root path 或穩定 User-0 HOME replacement。

逐列固定欄位（含 hashes、exact paths、method/offset、status、next safe step）見 companion CSV：[`luna_worker_ps7331_residual_writer_inventory_20260810.csv`](./luna_worker_ps7331_residual_writer_inventory_20260810.csv)。

## Integrity / validation

CSV 以 `sha256sum` 於本輪產出後計算；本檔與 CSV 的最終 SHA-256 會在下方補記。所有 evidence hashes 均沿用既有 Phase 6 artifact/index；若來源 hash 與現存檔案不一致，應標為 provenance discrepancy，不得擴張結論。

- device contacted: false
- Binder/service/broadcast dispatched: false
- OTA/updater/recovery executed: false
- root/exploit/ioctl/reboot/partition write: false

Output hash (CSV, after final edit): `967b23450726a54e0fba2bb00e587e2d16d3451f365b7503c2c0d4e62bbbbba5`.
