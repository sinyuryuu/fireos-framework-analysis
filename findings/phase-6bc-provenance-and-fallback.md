# Phase 6BC：PS7331 Provenance、OTA/IPC 邊界與 fallback rollback

## 範圍與安全狀態

本階段分成兩部分：

1. 主機端稽核 PS7331 官方 source、OTA script、保存的 VDEX/Java source。
2. 對既有研究用 redirect APK 做一次可恢復的清理驗證。

沒有執行 root exploit、GhostLock race、未知 Binder transaction、OTA/recovery、
crafted package、分割區寫入、remount、SELinux 修改，也沒有停用、隱藏、suspend、
解除安裝或清除 `com.amazon.firelauncher`。

原始裝置快照保留於本機 `adb/phase6bc/PHASE6BC-REDIRECT-STATE-20260805-01/`，
因含裝置序號而不納入公開 commit。主機端 audit 產物保留於：

`artifacts/phase6bc/ps7331-provenance-control-20260805-02/`

## Executive summary

### 已證實

- PS7331 官方 source scope 含 MT8183/trona 的 kernel source 與 defconfig，
  但不含 `platform/system/core/init/selinux.cpp`、Android framework source
  tree，亦沒有 Fire Launcher implementation source。
- source focus 的重要 hash 已由 audit 產生；完整 source archive、OTA 與 boot
  image 的版本 provenance 另由既有 Phase 5/6 artifact 保存。
- OTA Java path 對 sideload 檔案採 basename staging，並使用 `renameTo`／
  copy-delete fallback；`SideloadVerifier`、metadata/device-state checks 及
  privileged controller 邊界仍在安裝鏈上。這是高影響靜態 review surface，不是
  已證明的 exploit。
- `BootAfterSystemOTAReceiver` 是 OTA/OOBE lifecycle path，可能啟用 priority-100
  的 `OobeHomeActivity` 並修改 setup state；沒有在設備上人工 replay。
- `preWarmApplicationForUser()` 的保存 disassembly 顯示 permission-check 後
  緊接 identity clear，再到 `startProcessLocked`。這是靜態授權 anomaly candidate；
  shell 在 Enforcing capture 中沒有 private service handle，也沒有執行 Binder。
- 清理後設備狀態正常：研究 APK 不再存在、Accessibility enabled service 為空、
  `accessibility_enabled=0`、HOME resolver 與前景回到 Fire Launcher、ADB 仍為
  `device`。

### 高可信推論

- 目前「Fire Launcher 不能由 shell enabled-state mutation 停用」的最佳解釋仍是
  PS7331 PackageManager protected-package gate 與 Amazon deny-list callback；本階段
  沒有觸碰該 gate，也沒有重複已被排除的 component-disable 測試。
- OTA/OOBE、Amazon private Binder 與 KFT package-state 路徑都位於 privileged、
  system-server 或 lifecycle 邊界，不能當成普通 ADB launcher replacement。
- 既有 Accessibility redirect 是近似 foreground redirect，不是正式 HOME；保存的
  Phase 4 測量為 0/30 reliable foreground handoffs，因此目前不列為穩定方案。

### 已排除／因風險拒絕

- **已排除：** 本階段沒有證據支持 source archive、OTA staging、prewarm 或
  `BootAfterSystemOTAReceiver` 可直接提供 root 或正式 HOME replacement。
- **因風險拒絕：** 讀取 system-owned deny-list 內容、手動發送 OOBE action、啟用
  `OobeHomeActivity`、呼叫 private Binder transaction、執行 OTA/recovery、測試
  malformed/symlink payload、任何 Fire Launcher mutation。

## 1. PS7331 provenance

### 版本輸入

| Artifact | Provenance / hash | 判定 |
|---|---|---|
| Official source archive | `Fire_HD10-7.3.3.1-20250617.tar.bz2`；`02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` | 已證實既有 provenance |
| Nested platform source | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` | 已證實既有 provenance |
| Nested Fire OS source | `bb7030296545dd45edcf47d3e742043e7813852844f4b0fbbe8d223899b369` | 已證實既有 provenance |
| Official PS7331 OTA | `update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin`；`9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` | 已證實既有 provenance |
| Extracted PS7331 boot image | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` | 已證實既有 provenance |

本階段 `audit_phase6bc_provenance.py` 預設使用既有 hash manifest，不重新讀取
數 GB archive；因此 audit JSON 的 `hash_verified_now=false` 是刻意的 provenance
標記，不應解讀成此次重新 hash 已完成。

### Source scope

| Focus | SHA-256 | 結果 |
|---|---|---|
| `platform/kernel/mediatek/mt8183/4.4/kernel/futex.c` | `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96` | PRESENT |
| `platform/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | PRESENT |
| `platform/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig` | `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac` | PRESENT |
| `build_kernel.sh` | `3b7804c62d8533e200c54f076de4e0382bb21c5e924bbc8ac34773ce98653e33` | PRESENT |
| `build_kernel_config.sh` | `fbf0f922fad86ac34d94a1c9c1587cb618516191b4e101b990d757e356b97cfa` | PRESENT |
| `platform/system/core/init/selinux.cpp` | — | ABSENT in extracted scope |

這只證明官方 source package 的範圍；不能把「沒有 Android framework source」寫成
「Fire OS framework 沒有修改」。framework／system-server 結論仍以既有 VDEX、APK、
smali 與 AOSP 對照報告為準。

## 2. OTA / post-install control surface

既有 source-level evidence：

```text
SideloadVerifier
  → metadata / device-state / recovery verification
  → SideloadInstaller
  → SideloadMover.maybeMoveSideloadFile()
  → /data/ota_package/<basename>
  → UpdateSystemWrapper.install()
  → privileged OTA/recovery path
```

關鍵位置：

- `SideloadMover.java:31-44`：由輸入檔名取 basename，建立 OTA external-data
  destination。
- `FileHelper.java:61-64,305-339`：`FileOutputStream` copy fallback、`renameTo`、
  copy+delete 與 MD5 collision handling。
- `SideloadVerifier.java:31-68`：sanity、metadata、recovery package verification
  與 device-state check。
- `SideloadInstaller.java:65-84`：驗證完成後才 move 與 hand-off。
- `UpdateSystemWrapper.java:33-44`：寫入 OTA screen-state 並呼叫
  `UpdateSystem.install`。

判定：這是應保留的 host-only code review surface。沒有在 retail device 上把
檔案送入 staging、沒有執行 updater/recovery，也沒有嘗試 traversal、symlink 或
malformed payload。

## 3. Amazon IPC / OOBE boundary

### `preWarmApplicationForUser`

保存指令流的位置：

`decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:40453-40534`

局部鏈：

```text
checkCallingPermission("com.amazon.permission.APP_PREWARM")
  → clearCallingIdentity()
  → getApplicationInfo()
  → PreWarmCacheHelper
  → startProcessLocked(..., "prewarm", ...)
```

`checkCallingPermission` 結果未在保存的局部指令流中看到消費，是 **Strong
evidence / static anomaly candidate**，不是 live primitive。已知保存 caller 是
privileged Alexa path；shell 的 `service_manager find` 在 Enforcing 下被拒絕。

### `BootAfterSystemOTAReceiver`

這條鏈是：

```text
system_server boot phase 550
  → PackageManagerService.isUpgrade()
  → BOOT_AFTER_SYSTEM_OTA (protected OTA/OOBE lifecycle)
  → BootAfterSystemOTAReceiver
  → OOBE predicates
  → enable OobeHomeActivity (priority 100)
  → OOBEActivationHelper / setup-state writes
```

它不是普通 shell HOME selector。手動 broadcast、直接 enable component、改寫
OOBE settings 都可能改變 setup/navigation 狀態，列為風險拒絕。

## 4. 可恢復實機 rollback

### Before

Test ID：`PHASE6BC-REDIRECT-STATE-20260805-01`

在清理前，設備上仍可看到兩個既有研究 APK：

- `org.fireosresearch.phase4.redirect`
- `org.fireosresearch.phase4.alias`

Accessibility secure state 指向 redirect service；其可見控制頁顯示
`REDIRECT STOPPED`，也就是 service 設定存在但 redirect toggle 未啟動。
本次沒有啟用它，也沒有觸碰 Fire Launcher。

### Rollback

1. 透過原生 Accessibility Settings UI 對研究 service 執行使用者確認的停止
   操作。
2. 以 `pm uninstall --user 0` 移除上述兩個研究 APK。
3. 重新收集 package、Accessibility、activity、HOME resolver 與 ADB 狀態。

### After

本機 after snapshot：

`adb/phase6bc/PHASE6BC-REDIRECT-STATE-20260805-01/after-rollback/`

觀察結果：

| Check | Observed result | Confidence |
|---|---|---|
| Test APK path | 兩個 `pm path` 均無輸出 | Confirmed, cleanup scope |
| enabled Accessibility service | 空值 | Confirmed |
| `accessibility_enabled` | `0` | Confirmed |
| HOME resolver | `com.amazon.firelauncher/.Launcher`, priority 50 | Confirmed |
| top/resumed Home | `com.amazon.firelauncher/.Launcher` | Confirmed |
| ADB transport | `device` | Confirmed |
| Fire Launcher package/component | 未執行任何 mutation | Confirmed by command scope |

之後用 `input keyevent 3` 將前景返回 Home，沒有使用 settings write、Fire package
mutation 或重開機。

## 5. 公開結論

目前最精確的結論是：

1. **Fire Launcher 強制選擇：** 已有證據仍指向 PackageManager 的 privileged
   priority 50 candidate，加上 Amazon protected-package／system-app 邊界；本階段
   沒有新的 HOME resolver mutation。
2. **OTA/OOBE：** 存在高影響 lifecycle control surface，但不是安全的第三方
   launcher 或 root 入口。
3. **Amazon private IPC：** 有值得 code-review 的 prewarm permission-check
   anomaly candidate，但 service visibility、caller provenance 與沒有 live
   invocation 的事實都不支持把它當成可用提權路線。
4. **Fallback：** 現有 redirect APK 已安全清除；正式 HOME replacement 仍未找到。
   近似方案只有使用者主動的 explicit launch／shortcut。既有 Accessibility
   implementation 的 0/30 結果不支持把它列為穩定 workaround。

## Reproduction

### Host-only audit

```sh
python3 tools/scripts/audit_phase6bc_provenance.py --dry-run
python3 tools/scripts/audit_phase6bc_provenance.py \
  --source-root firmware/extracted/PS7331-SOURCE-20250617 \
  --source-archive firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2 \
  --ota firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin \
  --updater-script firmware/extracted/PS7331/META-INF/com/google/android/updater-script \
  --services-disassembly decompiled/baksmali/vdexExtractor/services/disassembly.log \
  --fosservices-disassembly decompiled/baksmali/vdexExtractor/fosservices/disassembly.log \
  --ota-source-root artifacts/phase6j/ota-apk-ps7331-jadx-20260805-01 \
  --ota-contracts-source-root artifacts/phase6j/ota-contracts-ps7331-jadx-20260805-01 \
  --output artifacts/phase6bc/ps7331-provenance-control-YYYYMMDD-NN \
  --source-archive-sha256 02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea \
  --ota-sha256 9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5
```

命令預設拒絕覆寫非空 output；加 `--verify-large-hashes` 才會重新讀取大型
archive。它永遠不連接設備、不執行 updater、不建構 OTA payload。

### Read-only / rollback evidence

原始 command、stdout、stderr、exit code 與 SHA-256 manifest 在本機
`adb/phase6bc/PHASE6BC-REDIRECT-STATE-20260805-01/`。公開版只引用其 evidence
scope，不公開裝置序號。
