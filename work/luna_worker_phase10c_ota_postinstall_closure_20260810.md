# Phase 10C：PS7331 OTA/update-binary/post-install closure

日期：2026-08-10。範圍限 host-only 靜態分析；未下載、構造或執行 OTA，未進入 recovery/sideload/flash/reboot，未做 symlink/malformed-input 測試、partition write、Binder/driver/root/exploit 操作。

## 最小結論

- `BootAfterSystemOTAReceiver` 與 `AmazonPackageManager.onBootPhase(550)` 的 caller/lifecycle gate 已接到受保護的 `BOOT_AFTER_SYSTEM_OTA` 流程；sink 是 OOBE component/settings，不是已證實的普通 Fire HOME writer。receiver 的數字 user scope 與完整 runtime protected-broadcast union 仍 UNKNOWN。
- `DeviceSoftwareOTA` 的 `OtaService` 為 exported 但受 `com.amazon.dcp.ota.permission.CONTROLLER`（`signature|privileged`）保護；`IOTAControlService.installSideload`、`SideloadMover`、`FileHelper`、`UpdateSystem.install` 只形成受 gate 的 privileged capability。普通 app/shell caller 未閉合。
- `RecoverySystem.verifyPackage`、hash/metadata/device checks 位於 Java validation path；`UpdateSystem.install` 是 recovery/native handoff。平台 verifier、AVB、rollback index、slot/SELinux 與 authoritative post-install executor 未在保存 corpus 完整閉合，標 `UNKNOWN`。
- `update-binary` indirect registry 與 fixed updater-script entrypoints 可接到 `WriteToPartition → ota_open/ota_write → open/write`；`CacheSizeCheck → MakeFreeSpaceOnCache → readlink/stat/unlink` 是 cache capability。未證明不可信 input 可控制 path，也未觀察任何 effect。
- 在 bounded corpus 中，沒有普通 app 或 shell 可合法導向高權限 OTA/update-binary/partition sink 的完整 caller chain；此為 `NEGATIVE_BOUNDARY_BOUNDED`，不是 binary-wide absence。

## CSV

逐列 evidence、caller、gate、Binder identity、user/partition scope、sink、effect、status 與 missing edge 見 [phase10c CSV](./luna_worker_phase10c_ota_postinstall_closure_20260810.csv)。CSV 共 12 rows，欄位符合要求。

CSV SHA-256：`07f58b1084fc49959e77472c93ac2a63bbc22f831eb4104e306aa0ab00556608`

## Evidence boundary

本 summary 只整合既有 Phase 6MY/6MZ/6NB 相關保存 artifacts，未重做固定 updater inventory；所有未解析的 caller、canonicalization/NOFOLLOW、recovery/native handoff、AVB/rollback 與 observed effect 保留 `UNKNOWN`。
