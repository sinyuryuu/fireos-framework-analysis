# Phase 6AT：PS7331 runtime follow-up 與控制面結案更新

## 目的

本次更新把 PS7331 上一次受控的 Accessibility/PendingIntent foreground
measurement，與已完成的 Amazon IPC、PackageManager deny-list、HOME callback
及 OTA/OOBE 靜態分析合併。它不重做 Phase 3A–3C，也不把 foreground redirect
誤稱為正式 HOME replacement。

## 新增實機證據

### 已證實

| Evidence ID | Observed result | Confidence |
|---|---|---|
| PHASE5CQ-PS7331-001 | 20 次 probe 後送出 `KEYCODE_HOME`，20/20 foreground dump 仍為 `com.amazon.firelauncher/.Launcher`。 | 已證實 |
| PHASE5CQ-PS7331-002 | 測試 alias 在 20 次 foreground dump 中出現 0/20 次。 | 已證實 |
| PHASE5CQ-PS7331-003 | resolver 前後皆為 `priority=50 ... com.amazon.firelauncher/.Launcher`。 | 已證實 |
| PHASE5CQ-PS7331-004 | 測試沒有停用、隱藏、suspend、解除安裝、force-stop 或清除 Fire Launcher，也沒有 Settings provider write、未知 Binder、reboot 或 partition write。 | 已證實 |

公開去識別化證據位於：
`artifacts/phase5cq/public-summary-20260805-01/`。

逐次 foreground dump、原始命令與完整 logcat 保留在研究者本機的
`adb/phase5/PHASE5CQ-ACCESSIBILITY-PENDINGINTENT-PS7331-T01/`，不推送到公開
repository。

## 與既有靜態證據的合併判讀

### 已證實

- HOME key 的已稽核 bounded implementation 仍建立隱式
  `MAIN + CATEGORY_HOME` intent，交給正常 activity start/resolution path；
  沒有在該 method body 看到 Fire Launcher explicit component。
- PS7331 的 `amazon.fireos` package deny-list resource 含有
  `com.amazon.firelauncher`，並連到 protected-package callback 路徑。
- 保存的 enforcing-policy evidence 中，shell UID 對選定 Amazon private
  services 的 service-manager lookup 被拒絕；service inventory 不等於 shell
  可取得 Binder handle。
- `BootAfterSystemOTAReceiver` 是受保護的 post-OTA/OOBE lifecycle surface，
  不是普通 shell HOME selector；其 broadcast、OOBE state mutation、updater、
  recovery 與 partition path 均未 replay。

### 高可信推論

目前最小且一致的模型是：Fire Launcher 的 privileged/system candidate 與
effective priority 50 先使標準 HOME resolver 選中它；Amazon package-protection、
task visibility 及 private-service SELinux boundary 是分離的控制面。這次
PS7331 0/20 foreground measurement 也不支持把 Accessibility/PendingIntent
當成穩定替代路徑。

### 已排除（目前安全範圍）

- 這個 Accessibility/PendingIntent 組合不是可持久的 Home-key redirect。
- 它沒有改變 formal HOME resolver。
- `BootAfterSystemOTAReceiver` 不能被當成可直接呼叫的第三方 launcher switch。
- Amazon private Binder service 的存在不能被當成 shell IPC bypass。

### 待驗證

- 其他不同的、明確由使用者授權的公開替代方案，仍需各自測量；本次 0/20
  不足以否定所有輔助方案。
- 完整 stripped/native callback closure 與自然官方 OTA 後 OOBE event ordering
  仍不是目前 live evidence。
- 尚未建立任何 root、privilege transition 或 kernel memory primitive。

## 裝置回復狀態

本次 runner 要求由研究者在 Settings 手動關閉 Accessibility service 及研究
App 的 redirect toggle，才能執行既有 rollback phase 移除兩個研究 APK。公開
artifact 明確標示 `manual_accessibility_rollback=pending`；因此本報告不宣稱
裝置已完成 rollback。這個狀態不涉及 Fire Launcher package 或資料。

## 下一個最小安全目標

先完成上述人工 Accessibility 關閉與 runner rollback，保存 after snapshot；
再只做 host-only 的 method-level closure 或 source/boot provenance。除非出現
新的 caller、permission 或不同控制條件，不再重複本次等價的 0/20 foreground
redirect 測試。

## 重現

```sh
python3 tools/scripts/build_phase5cq_public_summary.py --dry-run \\
  --source adb/phase5/PHASE5CQ-ACCESSIBILITY-PENDINGINTENT-PS7331-T01 \\
  --output artifacts/phase5cq/public-summary-20260805-02
python3 tools/scripts/build_phase5cq_public_summary.py \\
  --source adb/phase5/PHASE5CQ-ACCESSIBILITY-PENDINGINTENT-PS7331-T01 \\
  --output artifacts/phase5cq/public-summary-20260805-02 \\
  --redirect-apk tools/phase4-accessibility/dist/20260804-keyevent-pendingintent-jdk17-01/org.fireosresearch.phase4.redirect.apk \\
  --alias-apk tools/test-launcher-phase4/dist/20260803-openjdk17-03/org.fireosresearch.phase4.alias.apk
(cd artifacts/phase5cq/public-summary-20260805-02 && shasum -a 256 -c sha256sums.txt)
```

第二個 output 目錄僅是重新產生的新 artifact；既有公開 artifact 不會被覆寫。
