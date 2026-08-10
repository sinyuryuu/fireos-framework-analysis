# Phase 21D — deny-list evidence boundary

日期：2026-08-10（Asia/Taipei）  
輸入：`P20D-DENYLIST-004`。  
範圍：只讀 host artifact/hash/schema/path comparison；本輪未執行 ADB、live privileged read、chmod、Arcus refresh、Binder、Fire Launcher mutation 或任何裝置操作。

## 結論

| 層 | 判定 | 可由已保存證據閉合？ |
|---|---|---|
| Resource seed | PS7331 `amazon.fireos:raw/package_manager_deny_list` 的 path/resource ID/schema 與 raw JSON membership 已閉合；`com.amazon.firelauncher` 明列一次 | **YES — host-static closed** |
| Persisted membership | `/data/system/PackageManagerDenyList` 的檔案存在、大小、owner/mode/time 與讀取被拒絕已保存；`DenyListKeyPackages` literal set content 沒有保存 | **NO — content remains unknown** |
| Observed protected rejection | Fire package 與 component 的 shell mutation 都保存 `SecurityException: Cannot disable a protected package`，且 post-state 顯示 Fire enabled / HOME unchanged | **YES — runtime observation closed** |
| Resource → persisted → rejection join | static consumer chain 與 runtime rejection 互相一致，但缺 live persisted literal membership，不能把整條鏈宣稱為 live content proof | **PARTIAL only** |

## P21D reconciliation IDs

### `P21D-RESOURCE-001` — resource seed（closed）

已保存 host artifact：

- `artifacts/phase6ap/denylist-resource-closure-20260805-01/resource-table-targets.json`
  將 resource ID `0x7e05000a`（decimal `2114256906`）映射至 package ID `0x7e`、package `amazon.fireos`、type `raw`、entry `package_manager_deny_list`，path `/system/framework/fireos-res/fireos-res.apk`。
- `res/raw/package_manager_deny_list.json` 是合法 JSON object；`packages_deny_list` 是 string array，共 48 entries、46 unique；`com.amazon.firelauncher` 出現 1 次。
- `summary.json`、`input-sha256.json`、`package-table.json`、`resource-table-targets.json`、`debugfs-commands.json` 均可 parse；artifact `sha256sums.txt` 全部通過。
- raw JSON SHA-256：`16086fecbfce0a20c0b37535e25d690635d398b30d582fa6d231736dc9bdf710`。
- extracted `fireos_res_apk.apk` SHA-256：`699e3b5e6ee5e7f9cc97be06d815b029af9456ef36606b0a0c62f4be789bb188`。
- source `fosservices/disassembly.log` 的保存 snippet 顯示 `Resources.getSystem().openRawResource(0x7e05000a)`、JSON key `packages_deny_list`、以及缺少 `DenyListKeyPackages` 時的 `putStringSet(...).commit()` seed branch。

可安全結論：**resource seed source、resource schema、host artifact membership 已閉合**。這不等於 persisted file 已被讀出，也不等於 seed branch 在該 device boot 時必然執行；seed branch 是 conditional-on-key-absence。

### `P21D-PERSISTED-002` — persisted membership（未閉合）

已保存的 live evidence 只有：

- `/data/system/PackageManagerDenyList` 存在，size `2645` bytes，owner/group `system:system`，mode `0660`，以及保存的 access/modify/change timestamps。
- `deny_list_shared_pref_ls.stdout.txt` 沒有提供 XML/content listing。
- `pull_path__data_system_PackageManagerDenyList.log` 明確保存：`adb: error: failed to stat remote object '/data/system/PackageManagerDenyList': Permission denied`。
- Phase 6AI static consumer 顯示 reader 使用 device-protected `SharedPreferences` file basename `PackageManagerDenyList`，key `DenyListKeyPackages`；但這是 reader/writer code evidence，不是 persisted set content。
- 歷史 Phase 6DK Arcus trigger 的 before/after stat 相同、inode/time/size 未變；這只證明該保存 capture 沒觀察到 metadata change，不提供 set literal。

可安全結論：**persisted file metadata/ACL boundary 已閉合；persisted `DenyListKeyPackages` membership 未閉合**。不能把 host raw resource 的 Fire membership、static `putStringSet` branch，或 protected rejection 反推成 live persisted literal membership。

### `P21D-REJECTION-003` — observed protected rejection（closed as observation）

保存的 `adb/phase6fg/PHASE6FG-PMS-PROTECTED-PACKAGE-20260806-01/command-output.txt` 包含兩個歷史命令：

- `adb -s G001LT0511550CFT shell pm disable-user --user 0 com.amazon.firelauncher`
- `adb -s G001LT0511550CFT shell pm disable-user --user 0 com.amazon.firelauncher/.Launcher`

兩者都回傳：`Security exception: Cannot disable a protected package: com.amazon.firelauncher`，stack 進入 `PackageManagerService.setEnabledSetting()`，分別經 `setApplicationEnabledSetting()` 或 `setComponentEnabledSetting()`。保存 post-state 顯示 `installed=true hidden=false suspended=false stopped=false enabled=0`，HOME resolver 仍為 `com.amazon.firelauncher/.Launcher` priority 50。

這一層可宣稱：**在保存的 exact-build runtime capture 中，shell package/component mutation 被 protected-package gate 在 state write 前拒絕，且 Fire/HOME post-state 未變**。不能宣稱：live deny-list literal 已讀出、所有 protected operations 都由同一 callback 結果造成、或存在任何 privileged bypass。

## Static chain status

保存的 Phase 6AI flow 將鏈條分段標為：

```text
PS7331 system.img
  -> fireos-res.apk resource table
  -> 0x7e05000a / package_manager_deny_list
  -> packages_deny_list JSON
  -> conditional seed: DenyListKeyPackages (only if key absent)
  -> ControlProtectedPackagesCallback reads persisted set
  -> vendor callback fan-in
  -> PMS protected-package decision
  -> observed shell rejection
```

其中前三段與 host seed membership為 `Confirmed`；reader/writer/conditional seed code為 `Confirmed static`；PMS rejection為 `Confirmed runtime observation`；中間的 **live persisted set literal** 是唯一未閉合的 evidence boundary。

## 不執行清單

本階段明確沒有、也不授權：

- live privileged read/pull of `/data/system/PackageManagerDenyList` 或 `DenyListKeyPackages`；
- `chmod`、remount、SELinux bypass、Arcus refresh/broadcast、property mutation；
- Binder/service call、ADB 新 capture、Fire Launcher disable/enable/uninstall/force-stop 或 HOME mutation；
- OTA/recovery/root/partition 操作。

這些缺口保持 `UNKNOWN`，不是 negative runtime result。

## Validation performed

僅在 host 上完成：JSON parse/schema check、entry/unique/Fire count、resource/path comparison、存在性檢查，以及既有 SHA-256 manifest verification。沒有重新執行 artifact extraction，也沒有接觸裝置。

## Evidence paths

`artifacts/phase6ap/denylist-resource-closure-20260805-01/`；`artifacts/phase6ap/consumer-snippet-20260805-01/`；`artifacts/phase6ai/denylist-flow-20260805-01/`；`output/tables/phase6ap-denylist-resource.csv`；`output/tables/phase6ai-denylist-flow.csv`；`artifacts/phase6k/readonly-device-20260805-01/deny_list_*`；`firmware/manifests/ARTIFACT-20260803-04/pull_path__data_system_PackageManagerDenyList.log`；`adb/phase6fg/PHASE6FG-PMS-PROTECTED-PACKAGE-20260806-01/command-output.txt`；`adb/phase6dk/PHASE6DK-DENYLIST-ARCUS-BROADCAST-20260806-01/{result.md,metadata.json}`。
