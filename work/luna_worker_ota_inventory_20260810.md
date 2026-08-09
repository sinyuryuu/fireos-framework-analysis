# PS7331 OTA / OOBE / recovery verifier inventory

日期：2026-08-10。角色：`luna_worker`。本報告只整理既有主機端檔案與已保存的唯讀證據；未連接設備、未執行 ADB/Binder/broadcast/OTA/recovery/updater、未修改 package/settings/partition，未提交或推送。沒有提出 malformed OTA、symlink、partition write、private Binder replay 或 root exploit。

## 總結結論

1. **只有 capability、沒有 shell/普通 app 可達證據：** PS7331 `update-binary` 可靜態註冊 recovery commands、抽取檔案並寫入 named partitions；`updater-script` 也列出 system/vendor/boot chain 等目標。但既有 Java 驗證→`UpdateSystem.install` 與 recovery/native updater handoff 是分開的 provenance boundary，沒有建立 shell 或 ordinary-app caller。這是高權限 capability，不是 ADB workaround。
2. **OOBE/BootAfterSystemOTA：** system-server 在合法 post-OTA upgrade 條件下發送受 permission 保護的 action；receiver 可寫 setup/OOBE state、enable `OobeHomeActivity`。這不是一般第三方 HOME replacement；目前保存狀態仍是 Fire Launcher 正常 HOME、OOBE Home disabled。人工 replay 已明確拒絕，因為會改變 setup/foreground state。
3. **recovery verifier：** Java path 明確呼叫 `RecoverySystem.verifyPackage` wrapper，並有 metadata/version/signature/PVT checks；平台 recovery verifier 的完整 native implementation 與 updater handoff 尚未在保存輸入中閉合。不能把 wrapper 存在解讀成 shell 可達或 verifier bypass。
4. **唯一不重複的主機端缺口：** `PerformBlockImageUpdate → CacheSizeCheck` 已有 direct caller edge；`CacheSizeCheck` body、`MakeFreeSpaceOnCache` 的完整 callers、其 canonicalization input/output、function-pointer dispatch 與 return/error dataflow 尚未完整選取。既有 bounded negative 只表示 selected graph 沒有 direct canonicalization→write edge，不能擴大為 binary-wide absence。

## Evidence inventory

| Evidence ID | 檔案（含位置） | SHA-256 | 結論與信心度 | 建議 |
|---|---|---|---|---|
| 6K-OTA-001 | `findings/phase-6k-evidence-index.md`；SideloadMetadataChecker/SideloadVerifier | `eca26639df789835bdd21357ef4114a38f7cc4bb7a32bdf247dde65576042f99`；來源 hash 見報告 | OTA metadata、build/product/signature/PVT 與 `RecoverySystem.verifyPackage` 靜態鏈；**已證實** | 保留為 OTA verifier Java-side provenance；不執行 sideload/recovery。 |
| 6K-OOBE-001 | `findings/phase-6k-evidence-index.md`；`BootAfterSystemOTAReceiver.java:21-80` | `eca26639df789835bdd21357ef4114a38f7cc4bb7a32bdf247dde65576042f99`；receiver `c29b32bf6874b245859357d926773193c15771a6eb254f97edac57541ae5cb90` | action 命中後可寫 OOBE prefs、enable OOBE Home、activate OOBEIF；**已證實靜態流程** | 僅做既有 source/dataflow 整理；不 replay action。 |
| 6M-OOBE-001..008 | `findings/phase-6m-evidence-index.md` | `8eea479b2dea0ab2b8219bee2b9a3b825208f9dd0ff313f3c05cb5006c671933` | sender phase 550 + `isUpgrade()`、receiver side effects、priority-100 HOME/SETUP_WIZARD、OTA controller permission boundary 均已記錄；**已證實/高可信** | 不重做 OOBE receiver、OTA controller 或 file-flow inventory。 |
| 6Q-OOBE-001..002 | `findings/phase-6q-evidence-index.md` | `7b0d41854897b297ebca37f438b74f45b0feecdff49bd8d3cf84c51ef853c738` | system-server sender 與 receiver setup mutation；**已證實** | 不以 action 名稱推導 public caller；維持 lifecycle boundary。 |
| 6R-OOBE-001..010 | `findings/phase-6r-evidence-index.md` | `fc51d7b8fe40f7c5eb8f89f40ef0bfe187f02b64637fdcc07168f7443e295b6c` | `RECEIVE_BOOT_AFTER_SYSTEM_OTA` 為 `signature|amazon`；receiver permission argument 不是 sender authentication；additional Alexa consumers 存在；**已證實** | 不重複 protected-broadcast membership；不發送 broadcast。 |
| 6MY-001 | `findings/phase-6my-ota-receiver-package-helper-closure.md` | `3977b4cef2d000c3b598b1d582719374ef8cb230055fcec6e98b36e0db4e15bb` | `onBootPhase → receiver → PackageHelper.setComponentEnabledSetting(state=1) → OOBE Home`，且沒有 Fire Launcher/HOME writer reference；**bounded static confirmed** | 可做的剩餘工作只有 context/user-scope host trace；不改 component/settings。 |
| 6P-OTA-001..004 | `findings/phase-6p-native-updater-closure.md`；官方 `update-binary`、`updater-script` | report `5c189b56c5cd9f79a47254368c9737a95a4ba72bd34365ae7d867beea654474e`；binary `02643fa987778361742a5ecaa601034b7f20a55df9bacc58ec8bbcdcd8ac896b`；script `4a61d66754187a5b84f173ad7bc50216b00969743ce3193346762613615ac248` | `PackageExtractFileFn`、`WriteToPartition`、`ota_open→open`、`VerifyBlocks` 及 fixed partition targets；**高權限 capability confirmed** | 不把 capability 當 reachability；不執行 ELF、recovery 或 partition operation。 |
| 6P-PATH-001 | `findings/phase-6p-native-updater-evidence-index.md`；`MakeFreeSpaceOnCache→__readlink_chk` | report hash 同上；canonicalization artifact `8cc6d38c1e464b6b741b29bdee8aa253113e7aea286f368ffe1cf1c0cde5983d` | readlink-family marker/callsite 存在；**static evidence，impact unproven** | 不構造 symlink/traversal；只允許 host-side argument/dataflow trace。 |
| 6KT-001 | `findings/phase-6kt-recovery-verifier-provenance.md`；`artifacts/phase6kt/recovery-verifier-audit-20260810-01/audit.json` | report `484273958f44898c6b94a208da4e144936df09a191e03efe6316c18d167fe732`；audit `01e29ec3a2649d85d033ce7ce65034631ebb44ef00633e34a95b0eb063f317f9` | Java verification/staging precedes normal install handoff；platform verifier implementation與 final native caller provenance未閉合；**strong evidence / unresolved boundary** | 只可做保存 artifacts 的 verifier/certificate/AVB provenance；不做 crafted OTA。 |
| 6MK-001 | `findings/phase-6mk-updater-dispatch-closure.md`；saved call-edge table | report `443c69127293d18903d469f7a670a4b58b208cdbf6402c240ecaeec6e307ecb3`；call edges `ede44312f2f667adff552475866de0b17c06b96161854c35a17a3a1c361eaa75` | 24/24 install callback registrations、`package_extract_file` 到 extraction/open direct edges；**已證實 capability** | 不重做 registry；不得把 command registry 當 shell API。 |
| 6MM-001 | `findings/phase-6mm-updater-blockimage-closure.md`；`canonicalization-call-sites.csv` | report `f0caa7e810d02f0022180371e0b564f2cef13cd19ed7320fde107a8073d58601`；artifact `8cc6d38c1e464b6b741b29bdee8aa253113e7aea286f368ffe1cf1c0cde5983d` | block-image 五個 handlers mapping、`MakeFreeSpaceOnCache + 0x478 → __readlink_chk`；selected graph 無 direct canonicalization→write edge；**confirmed + bounded negative** | 這是目前最小不重複缺口，不可宣稱 traversal/symlink 結論。 |
| 6MM-002 | `artifacts/phase6mm-updater-blockimage-20260810-01/selected-call-edges.csv`；`findings/phase-6mm-updater-blockimage-closure.md` | `2e5074f461127445bfcb5633840aff16e2284545245292b5999581d672e10d65` | `PerformBlockImageUpdate` 有兩個 direct call site 到 `_Z14CacheSizeCheckm`；`CacheSizeCheck` body 未納入；**confirmed caller, unresolved callee/dataflow** | 下一步只選取 `CacheSizeCheck` body、所有 callers、return/error branches、function-pointer provenance。 |
| 6KU-001 | `findings/phase-6ku-low-privilege-boundary.md` | `0301464b2d01ef21c7b35997a3478479c349736b894fa1cd955fab3af977be90` | ordinary prewarm sink 僅 process/resource effect；KFT tx3 被標準 PMS gates 擋下；private Amazon PM 無 HOME/package-state setter；updater 是 recovery-context capability；**已證實 boundary** | 不重複 prewarm/KFT/private PM；不發 private Binder。 |
| 6K/6Q-IPC | `findings/phase-6k-report.md`、`findings/phase-6q-evidence-index.md` | 6K report `3e54dc0a41d5a585c005c1728ae7004cca8c1a7e982f6e34c4afd90a050baf3d`；6Q index `7b0d41854897b297ebca37f438b74f45b0feecdff49bd8d3cf84c51ef853c738` | shell UID 2000 對 Amazon private activity/window 等 service-manager `find` 被拒；沒有 shell/ordinary-app HOME/root API；**confirmed for saved scope** | 不重複 service lookup、Binder replay 或 runtime mutation。 |

## 依優先問題整理

### 1) 只有高權限 capability、沒有 shell/普通 app 可達證據

- `update-binary` 的 parser/registered callbacks、`PackageExtractFileFn`、`WriteToPartition`、`ota_open→open`、`VerifyBlocks`，以及 script 的 named partition targets：**有 capability，沒有 shell/ordinary-app caller**。
- OTA controller/OtaService 的 Binder contract：**有 service/method inventory，但 controller permission 是 service boundary**；普通 app 不能因知道 transaction constants 而取得控制權。
- `BootAfterSystemOTAReceiver`：**有 lifecycle-triggered component/settings writer**，但不是 public HOME API；保存 live state 顯示 OOBE Home disabled。
- Amazon private IPC/KFT/prewarm：既有證據分別是 service visibility/PMS gates 或 process sink；沒有新的 User-0 Fire Launcher HOME writer。

### 2) 已明確拒絕或不應重複

- 不 replay `BOOT_AFTER_SYSTEM_OTA`、不修改 OOBE preferences、`user_setup_complete`、`device_provisioned`、`isOOBEActive` 或 component enabled state。
- 不執行 OTA、sideload、recovery、`update-binary`、Edify command 或自然/人工 OTA transition。
- 不提供或測試 malformed/downgrade/signature-transition OTA、symlink/traversal path、partition target、fastboot/root route。
- 不做 private Binder parcel replay、guessed transaction、service mutation；Phase 6K/6Q/6R/6KU 已足以表示 saved scope 的 shell/普通 app boundary。
- 不重複 Phase 6M OOBE/OTA controller、6P updater capability、6Q Binder inventory、6R OTA authorization、6MY PackageHelper closure；新報告只引用其 provenance。

### 3) 不重複的主機端靜態缺口

目前仍可合理追加、且不需要設備或危險輸入的只有：

1. 反組譯 `CacheSizeCheck` (`0x414720`) body，標出輸入參數、比較/return value 與 error branches。
2. 從保存的 call-edge/symbol/disassembly 檢索 `MakeFreeSpaceOnCache` (`0x417778`) 的全部 direct callers，並區分 direct、indirect-resolved、indirect-unresolved。
3. 追蹤 `CacheSizeCheck` return value 是否影響 `PerformBlockImageUpdate` 的 control flow，再對齊 `MakeFreeSpaceOnCache` 的 path/buffer/result 與 `WriteToPartition`；function-pointer table 只在主機端解析。
4. 將結果限縮為「caller → argument provenance → return/error branch → sink」的資料流圖。若仍無完整 chain，應將 OTA 路線標為 boundary closure candidate，而不是進行 runtime OTA。

**不應做的替代方案：** 不以 malformed OTA、symlink、traversal、partition write、private Binder replay 或 root exploit 來填補上述缺口；這些都超出本工作範圍且會跨越高權限/不可逆邊界。

## 最終判定

PS7331 OTA/recovery 路線目前是「**高權限 capability 已確認；低權限 reachability 未建立；recovery verifier/native handoff 尚有有限 provenance gap；CacheSizeCheck/MakeFreeSpaceOnCache caller-return dataflow 是唯一不重複 host-only 缺口**」。沒有證據支持普通 shell/app 透過 OTA、OOBE、updater 或 private IPC 取得 root、改寫 Fire Launcher HOME 或安全地替代 launcher。

