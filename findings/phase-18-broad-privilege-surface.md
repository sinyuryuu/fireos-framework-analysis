# Phase 18 — 廣域特權面與可達性閉合

日期：2026-08-10（Asia/Taipei）
目標：Fire HD 10 / `trona` / Fire OS 7.3.3.1 / PS7331 / Android 9
範圍：不只 HOME；凡是可能取得足以改變 package/component state、User 0 policy、UID、OTA/recovery、driver 或持久系統狀態的路徑。

## Executive result

**已證實：**目前沒有找到完整的「普通 APK 或 ADB shell → 權限／SELinux gate → system identity 或受信任 user scope → Fire Launcher/package-state、UID 0、分割區或 kernel memory sink」鏈。

**已證實：**KFT `IAmazonUserManager` transaction 3 的靜態實作確實會把 `UserInfo.id` 傳給 Tahoe、Fire Launcher 與 Launcher3 的狀態 writer；既有 `PHASE6FK` ordinary APK / User 0 實測在 PackageManager setter 前遭 `SecurityException` 拒絕，狀態與 HOME 未變。`PHASE6FJ` 對 User 10 則遭 `INTERACT_ACROSS_USERS` 拒絕。這些測試沒有重跑。

**高可信推論：**KFT tx3 是最接近「一旦有合法受信任 caller 就能改變 Fire state」的控制面，但 tx3 的 Stub 內未見 caller check 不能單獨證明 confused deputy；目前的有效邊界仍是 service-manager 可見性、PMS caller gate、跨 user gate 與實際受信任 client 集合。

**已證實：**`AmazonPackageManagerImpl` 的 enabled-state facade 保留 Binder caller identity，委派標準 PackageManager/IPackageManager；沒有把 ordinary caller 轉成 system UID 的 `clearCallingIdentity()` 代理。

**高可信推論：**OTA/update-binary、RPMB、ION、CMDQ、M4U、uinput、AUXADC 等存在不同程度的靜態能力，但「能力存在」不等於「普通 caller 可達」。目前只有 ION generic/MTK native caller 的靜態入口相對閉合；仍沒有 ordinary app/shell 到 driver sink 或 UID/HOME sink 的證據。

**因風險拒絕測試：**沒有執行未知 Binder transaction、私有 service payload、driver open/ioctl、Root／exploit、OTA/recovery、sideload、reboot、分割區寫入、Fire Launcher mutation 或 SELinux/service-manager 修改。

## 1. 方法與資料完整性

本階段由主機端靜態檢查、既有 Phase 1–17 證據整理，以及五條分工的 host-only worker 分析組成。Worker 隔離工作樹的原始檔未同步到主工作區，因此本報告只整合 worker 回報的 row-level 摘要，並保留原始證據路徑；沒有把隔離檔名冒充成本地已封存原始證據。可重現的整合表為：

- [phase18-broad-privilege-surface.csv](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/output/tables/phase18-broad-privilege-surface.csv)
- [phase18-privilege-surface-flow.mmd](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/output/call-graphs/phase18-privilege-surface-flow.mmd)
- [build_phase18_privilege_closure.py](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/tools/scripts/build_phase18_privilege_closure.py)

本階段沒有新增裝置狀態變更；因此不存在 rollback state。既有實機結果只以已封存證據引用，不重跑。

## 2. 最重要的 caller → gate → sink 結論

### KFT / Fire state

靜態鏈：

```text
IAmazonUserManager tx3
  → AmazonUserManagerService.BinderService.enableKftLauncher(UserInfo)
  → tryEnableKftLauncherComponent(UserInfo)
  → Tahoe FreeTimeLauncherActivity = ENABLED
  → Fire Launcher application = DISABLED
  → Launcher3 application = DISABLED
```

這是**真實的 system-side writer**，但不是 ordinary caller 的可用 writer。既有 User 0 實測保存了 PMS 的 caller `uid=10213` 與 `SecurityException`，拒絕發生在 package/component state 寫入前；User 10 實測則保存 `uid=10212` 與跨 user 拒絕。詳見 [phase-17-report.md](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/findings/phase-17-report.md)、[phase17-residual-privilege-surface.csv](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/output/tables/phase17-residual-privilege-surface.csv)、[PHASE6FK command output](/Users/bob/Documents/Codex/2026-08-03-fire-os-7-framework-amazon-fire/adb/phase6fk/PHASE6FK-USER0-TX3-20260807-01/command-output.txt)。

**判定：已證實 writer；已證實 ordinary User 0 route 被 gate 擋下；受信任 client 集合仍待驗證。**

### Amazon PackageManager facade

`setApplicationEnabledSetting()`、`setComponentEnabledSetting()` 與 preferred setter 只委派標準 PackageManager/IPackageManager，沒有清除 caller identity。這排除了「只要找到 facade handle 就自然取得 system UID」的推論，但不排除真正具 signature/privileged 權限的 Amazon client。

**判定：已證實 identity preservation；沒有 ordinary-to-system relay 證據。**

### Prewarm

既有 Phase 6ER 曾觀察 ordinary APK 透過 private service 造成短暫 process/resource effect，後續 static path 指向 `startProcessLocked(..., "prewarm", ...)`。它沒有改變 package state、HOME、UID 或持久權限。

**判定：已證實有限 process/resource deputy；不是 root 或 Fire-state sink。**

### OTA / OOBE / recovery

PS7331 是 signed、full、block OTA。`updater-script` 對 system/vendor 與 boot-chain/firmware target 具有 recovery/updater 寫入能力；Java verification/install 與 system-server `BOOT_AFTER_SYSTEM_OTA` lifecycle 也有靜態鏈。這些均由簽章、AVB／rollback、recovery UID/SELinux 與 boot-chain gate 包圍，沒有 ordinary app/shell → recovery/updater 的證據。

`BootAfterSystemOTAReceiver` 能在受信任的 post-OTA lifecycle 下啟用 OOBE component、寫 setup state；它不是可重播的普通 broadcast workaround。

**判定：受信任 lifecycle sink 已證實；低權限可達性未證實；recovery/partition 測試因風險拒絕。**

### Kernel / MTK driver surfaces

ION generic/MTK native library 與 ioctl caller 的靜態入口已找到；CMDQ、M4U、performance ioctl、uinput、AUXADC、RPMB、USB 與 Amazon diagnostic 仍缺一個或多個 shipped object、selected DTB/DTBO、ueventd/file_contexts/TE、native caller 或 runtime effect edge。所有 driver node/ioctl 都不在本階段實機嘗試。

**判定：靜態 capability 多數成立；普通 caller reachability 與權限提升 sink 未證實。**

## 3. 廣域控制面分類

| 面向 | 狀態 | 可支持的結論 |
|---|---|---|
| KFT tx3 | Strong evidence / Confirmed runtime boundary | 有 UserInfo-scoped package writer；ordinary User 0/10 既有實測被 PMS／跨 user gate 擋住 |
| PMS enabled-state | Confirmed | package/component mutation 受 caller、protected-package 與 user scope gate 約束 |
| Amazon PM facade | Confirmed | 不清除 Binder identity，不是 system-UID 混淆代理 |
| Amazon flags/metadata | Strong evidence | 有 signature|amazon writer，消費者不是 HOME 或 Fire package-state sink |
| Profile/input services | Hypothesis / open edge | 私有服務與 callback 存在，但 caller→gate→sink 尚未閉合 |
| Prewarm | Confirmed limited deputy | 只造成短暫 process/resource effect |
| OOBE/BOOT_AFTER_SYSTEM_OTA | Strong evidence | trusted lifecycle 可寫 OOBE component/settings；普通 caller 未證實 |
| OTA/updater | Strong evidence capability | recovery-only partition capability；低權限 handoff 未證實，禁止實測 |
| ION | Strong evidence static caller | native library/ioctl 入口存在；runtime、domain、heap/policy 未閉合 |
| CMDQ/M4U/uinput/AUXADC/RPMB/USB | Hypothesis | source/config/device capability 不能替代 shipped caller/policy/runtime 證據 |
| GhostLock/futex | Hypothesis | source/model premise 存在；stock runtime mismatch、memory effect、root 未證實 |
| BROM/bootloader/partition | Disproved for normal ADB; risk-refused for exploit/write | 不屬安全 shell 路徑；任何寫入／exploit 需獨立 Level 3 報告 |

## 4. 關於「只要拿到權限就能關閉」的校正

方向正確，但「任一 permission」不成立。對 Fire Launcher 的正式停用至少要同時滿足：

1. caller 被 PackageManager 的 protected-package 與 enabled-state gate 接受；
2. 目標是正確的 User 0 scope，而非只傳入任意 `UserInfo.id`；
3. caller 具備相符的 system/signature/privileged 或合法 device/profile-owner authority；
4. SELinux/service-manager、跨 user、DevicePolicy 與 package state persistence 沒有再擋住；
5. 若走 Amazon private service，該 service 的外部 client 集合與 identity handling 必須閉合。

因此本階段的最佳搜尋策略不是羅列更多 permission 名稱，而是對每個候選建立同一個可驗證格式：

```text
caller UID/domain
  → service discovery / exportedness
  → descriptor + transaction or public API
  → permission / caller UID / user-scope gate
  → clearCallingIdentity ordering
  → concrete sink
  → observed state change
```

缺一段只能標為 `Hypothesis` 或 `Probable`，不能稱為 privilege escalation。

## 5. 已排除與仍值得研究

### 已排除（bounded）

- 普通 shell/APK 直接以 enabled-state API 停用 Fire Launcher。
- 普通 APK 經 KFT tx3 改變 User 0 Fire state。
- User 10 的普通 APK 跨 user KFT relay。
- ordinary-to-system 的 AmazonPackageManager facade identity relay。
- preferred HOME record 單獨取代 Fire Launcher。
- prewarm 作為 HOME、package、UID 0 或 partition sink。
- 已檢查的 Android/MTK CVE、GhostLock、BROM/fastboot 寫入路線作為安全實機 POC。

### 待驗證（只限主機端或自然被動觀察）

- KFT tx3 的完整、合法受信任 client/reference graph。
- Profile/input service 的 concrete caller、permission 與 downstream consumer。
- driver 的 selected DTB/DTBO、實際 object/module、merged policy、native opener。
- OTA native recovery verifier、rollback/AVB authority 與 caller identity。
- 自然發生的 Alexa prewarm 事件；只能被動記錄，不製造 private Binder call。

### 因風險拒絕測試

- 猜測或 fuzz `service call` transaction/parcel。
- 任何 `open/ioctl`：`/dev/ion`、CMDQ、M4U、uinput、RPMB、USB 或其他 driver。
- 停用／hide／suspend／uninstall／clear Fire Launcher。
- Root exploit、GhostLock runtime trigger、BROM/BootROM、bootloader、fastboot、recovery、OTA sideload、reboot、partition write、remount、SELinux 修改。

## 6. 下一步建議

最高價值且仍安全的下一步只有 host-only closure：

1. 對 exact PS7331 corpus 補齊 KFT tx3 的 interface reference、合法 client、ServiceManager publication 與 signature/SELinux gate；
2. 對 ION/CMDQ/M4U/uinput/RPMB 等補齊 shipped ELF、selected DTB/DTBO、merged policy 與 caller domain；
3. 對 OTA 只做 verifier/metadata/native handoff 的離線 CFG；
4. 若沒有新的 caller→gate→sink 閉鏈，正式結案為「普通 App／shell 無已證實的權限取得路徑；Fire Launcher 不能以安全 ADB API 停用」，不要用更危險的實機觸發代替缺失證據。

## 7. Reproduction

```sh
python3 tools/scripts/build_phase18_privilege_closure.py --root . --verify-only
```

此腳本只驗證整合 CSV 的欄位、分類、Evidence path 格式與已存在檔案；不連接 ADB、不執行 Binder/driver、不中斷服務、不改變裝置。
