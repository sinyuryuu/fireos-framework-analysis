# Deny-list provenance follow-up — Phase 6V / 6AI / 6PW

日期：2026-08-10  
公開基準：`a51db9cbb`  
範圍：host-only 檔案搜尋與既有結果整理。

## Safety boundary

本次只讀取工作目錄內既有的 PS7331 extracted framework/resources、Amazon APK/JAR、decompiled/smali、system-config metadata、artifacts、findings、CSV 與 call graph。沒有接觸裝置、沒有執行 ADB、沒有讀取或寫入 system-owned deny-list、沒有 Binder、root、exploit、settings/package mutation。只新增本報告與同名 CSV；既有檔案未修改。

## Result

目前可閉合的是「PS7331 resource seed 的靜態 provenance」：

```text
PS7331 system.img
  -> /system/framework/fireos-res/fireos-res.apk
  -> 0x7e05000a = amazon.fireos:raw/package_manager_deny_list
  -> packages_deny_list contains com.amazon.firelauncher
  -> DenyListArcusHelper.processJSON()
  -> device-protected PackageManagerDenyList / DenyListKeyPackages
  -> ControlProtectedPackagesCallback
  -> PMS ProtectedPackages gate
```

這裡的 `com.amazon.firelauncher` membership 是 extracted PS7331 raw resource 中的直接靜態觀察，不是 live persisted file 的直接觀察。Live file 只觀察到 `/data/system/PackageManagerDenyList` 的 system-owned metadata（`system:system`, mode `0660`, size `2645`）；其內容與 `DenyListKeyPackages` set 沒有被讀取。因此不能把 protected rejection 改寫成「live literal membership 已讀出」。

## Provenance classification

| 節點 | 分類 | 結論 |
|---|---|---|
| `0x7e05000a` resource mapping | static mapping | PS7331 resource table 精確映射到 `amazon.fireos:raw/package_manager_deny_list`。 |
| raw JSON package entry | direct observation（host artifact） | JSON 的 `packages_deny_list` 明列 `com.amazon.firelauncher`。 |
| `DenyListArcusHelper.processJSON()` | static mapping | system resource JSON 讀取 `packages_deny_list`，形成 initial set；只在 key absent 時 seed。 |
| `PackageManagerDenyList` / `DenyListKeyPackages` reader/writer | static mapping | device-protected SharedPreferences；callback 讀 set，seed 與 Arcus refresh 寫 set。 |
| `ControlProtectedPackagesCallback` | static mapping | system/privileged package + set membership + caller UID 2000 才回傳 protected。 |
| Fire package/component rejection | direct observation（既有 runtime） | shell disable rejection 發生在 state write 前；這證明 gate 行為，不單獨證明 file membership。 |
| live persisted Fire membership | unknown | ACL-protected content 未被讀取；resource seed 與 rejection 只能形成高可信 provenance/inference。 |
| Phase 6PW current HOME | direct observation（既有 runtime） | User 0 仍解析 Fire priority 50；與 deny-list provenance 相關但不是 membership proof。 |
| restoration writer / HOME writer | unknown / not found in saved scope | deny-list flow 沒有證明 Fire Launcher restoration 或 HOME selection writer。 |

## Evidence and hashes

- PS7331 system image：`da8a935484de24251e890fbf4e7dd9155567ebe158fc255d43684ea14c62b1e5`
- extracted `fireos_res_apk.apk`：`699e3b5e6ee5e7f9cc97be06d815b029af9456ef36606b0a0c62f4be789bb188`
- extracted `res/raw/package_manager_deny_list.json`：`16086fecbfce0a20c0b37535e25d690635d398b30d582fa6d231736dc9bdf710`
- Amazon `fosservices/disassembly.log`：`ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- framework `services/disassembly.log`：`373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53`
- callback registration XML：`eb53e50cf72174eddcde25fd3538e4736d2cd4cb7866bab4e5bc2b70fc514286`
- live deny-list metadata stdout：`9f7ad63a2514d38b0b488ff69de9136f3de064c2c08ee1bc26d5fcbd89c4e76c`
- Phase 6PW `metadata.txt`：`3c1adbbe8bdbfcd2e322647203157a68d5d45ab854ac4a40001fc8b0cf5c3f16`
- Phase 6PW HOME resolver stdout：`d65b3f8990fb3a8907405d3785dd8cf2826570b92baccb5477f3502df47608f6`

## Phase 6PW relation

既有 Phase 6PW 唯讀 capture 記錄 UID 2000、SELinux Enforcing、User 0 與 `com.amazon.firelauncher/.Launcher` priority 50，且沒有 Binder transaction 或 mutation。其 follow-up 仍把 deny-list literal membership 分類為 pending。故 6PW 只提供 current-state context，不把 live membership 從 unknown 升級成 observed。

保存檔案中沒有 6PW artifact 提供 `PackageManagerDenyList` 內容；本報告不新增 literal membership claim。

## Safe next step

只有自然發生且獲授權的 system-owned artifact，或既有保存的 privileged read-only capture，才可閉合 live persisted membership。界線保持如下：

```text
resource membership = direct static observation
live persisted membership = unknown
protected rejection = direct runtime observation
rejection implies live membership = inference, not literal observation
```

不要讀、pull、chmod、replace 或 trigger refresh `/data/system/PackageManagerDenyList`；不要 replay Arcus/OOBE、Binder、root、exploit 或 package/settings mutations。
