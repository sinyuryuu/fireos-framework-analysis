# Phase 6SF — Amazon permission/package-state provenance

日期：2026-08-10。範圍限定為 host-only：保存的 PS7331 exact-build permission XML、privapp-permissions、sysconfig、manifest、VDEX/JADX，以及 Phase 6MC/6RY/6SB 證據。未執行 adb、service call、Binder transaction、settings/pm、APK/native/driver/OTA/recovery 或任何裝置操作；未修改既有檔案。

## 結論

`amazon.permission.ADD_RM_PKG_METADATA` 在保存的 exact-build permission XML 中確實有 declaration：owner 是 `android.amazon.perm`，raw `protectionLevel=0x80000002`（Android bit encoding 對應 `signature|privileged`）。因此，Phase 6RY/6SB 中「XML 未找到 declaration」是過時結論，應由本報告的 exact XML 行 1822 更正。

但 declaration 不等於 holder、grant 或 production caller。保存的 privapp XML、platform privapp XML、sysconfig 與 Phase 6MC holder census 沒有 exact custom-permission grant/holder row；這只能寫成 **bounded corpus 未找到**，不能寫成「確定不存在」。同理，requested/granted 的 exact package join 與 grant source 未在保存 corpus 中閉合，應為 `UNKNOWN`／`NOT_ESTABLISHED`。

服務路徑可精確閉合到 method-level gate 與 metadata sink：`AmazonPackageManagerService.BinderService` 的 tx1/2/4/5 分別是 metadata/flags remove/set，method block 讀取 `amazon.permission.ADD_RM_PKG_METADATA` 並呼叫 `AmazonApplicationFlags`，最後 `writeToFile`。這是 confirmed static metadata persistence，不是 HOME selector 或 preferred-activity writer。system-server publication slice 顯示 BinderService 以 service name 發布，但該 call 沒有 service-level permission argument；保存證據只足以確認 method-level check，不能聲稱有或沒有另一個 service permission boundary。

實際 production caller 仍未確定。boot-fosframework 的 `AmazonPackageManagerImpl` facade callsites 與 generated Binder contract/dispatch 證明 API edge，不是上游 production caller。Phase 6MC caller inventory 未提供完整 production caller universe；故 caller/UID/signing identity 保持 `UNKNOWN`。

## HOME/package-state 關聯

同一 permission-owner XML 另宣告多個 HOME-related permissions：

- `com.amazon.permission.RECEIVE_HOME_LONGPRESSED_ACTION`、`com.amazon.permission.RECEIVE_CUSTOM_HOME`：raw `0x80000002`；
- `amazon.intent.permission.HOME_PRESSED`：HOME/HOME_DOUBLE_PRESSED broadcast receiver permission，raw `0x12`；
- `com.amazon.permission.RECEIVE_HOME_LAUNCH_REASON`：raw `0x80000002`。

這些是 declaration/broadcast-reception facts，不是 preferred HOME mutation authority。framework facade 中 `replacePreferredActivity`、`replacePreferredActivityAsUser`、`setApplicationEnabledSetting`、`setComponentEnabledSetting` 是 separate delegate methods；在保存的 bounded linkage review 沒有找到 `ADD_RM_PKG_METADATA` → HOME/preferred/activity-enabled edge。這個結果標為 **bounded corpus 未找到**，不是「確定不存在」。

KFT/child lifecycle 的既有 6SB 證據另證實 child-scoped component/application state writer，但它使用 supplied `UserInfo.id`，不是由 ADD_RM metadata 自動變成 User-0 HOME selector；完整 runtime caller/authorization universe 仍未閉合。

## 權限欄位判讀

| 欄位 | 判定 | 證據邊界 |
|---|---|---|
| declaration | `CONFIRMED` | exact XML line 1822 |
| protectionLevel | `CONFIRMED` raw `0x80000002`；symbolic `signature|privileged` | exact XML encoding |
| grant/holder | `BOUNDED_NOT_FOUND`, hence `UNKNOWN` | privapp/platform privapp/6MC census 無 exact row；非全映像否定 |
| requested | `NOT_ESTABLISHED` | owner manifest 不是完整 package requested-permission census |
| granted | `NOT_ESTABLISHED` | 6MC summary 無 exact custom row；非 runtime denial |
| service permission | `NOT_OBSERVED` | publication call slice 無 permission argument；method-level gate confirmed |
| actual production caller | `UNKNOWN` | facade/Binder evidence 不足以上游 caller identity |
| first sink | `CONFIRMED` | AmazonApplicationFlags maps/XML writer |
| HOME/package-state bridge | `BOUNDED_NOT_FOUND` | bounded static linkage review；非全映像不存在 |

## 主要 source/hash

- `artifacts/phase6bk/protected-broadcast-union-20260810-02/manifests/018_android.amazon.perm.xmltree.txt` — `89e141fbf220b18a8fe4ca2a959119a3ea0915e158dd514677a5285951daefed`
- `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` — `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` — `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/permissions/privapp_permissions.xml` — `643cf114ed7d7b82a642fea650ed7d2f53b5dab2291e4f043c272cbe577df732`
- `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/permissions/privapp-permissions-platform.xml` — `0b30c1624ffdab6c5454746737a060157276da5d2bd43addc74cd3919ae4aad1`
- `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/system/etc/sysconfig/framework-sysconfig.xml` — `bd6e7c52f1c036be4a770bd3be06d0c3a237d05f97921f47c2f652de59ca8fc3`
- `artifacts/phase6mc-permission-holder-audit-20260810-05/permission-holders.csv` — `1f97fa825f8b7cd86f05653259ecf43359d496d15af4e21e0c53512274ebdb18`
- `artifacts/phase6mc-caller-provenance-20260810-01/caller-provenance.csv` — `fbb4f21dad1c3948bb3748fe7bcf652b6b136a6fb07e62cb4e7d7e6d51e1b11d`

CSV companion：`work/luna_worker_phase6sf_permission_20260810.csv`。欄位固定，所有資料列均含 source、source_sha256、line、confidence；以 RFC-style quoting 保存逗號與引號欄位。
