# Phase 5CQ：PS7331 Accessibility/PendingIntent 前景導向測量

## 範圍

本測試是在 PS7331 目標設備上，使用研究用 `AccessibilityService`、測試
Launcher probe 與既有 PendingIntent 路徑，觀察 Home key 後是否能把前景導向
測試 Launcher。它不是 HOME resolver 或 default-home 變更測試。

測試沒有停用、隱藏、suspend、解除安裝、force-stop 或清除 Fire Launcher，沒有
寫入 Settings provider，沒有呼叫未知 Binder transaction，也沒有重開機或寫入
分割區。測試 APK 只屬研究用套件。

## 結果

### 已證實

- 測試 ID：`PHASE5CQ-ACCESSIBILITY-PENDINGINTENT-PS7331-T01`。
- 20 次迭代均在測試 probe 後送出 `KEYCODE_HOME`。
- 20/20 次前景 dump 都觀察到 `com.amazon.firelauncher/.Launcher`。
- 測試 alias 在前景 dump 中出現 0/20 次。
- HOME resolver 在測量前後都回傳：
  `com.amazon.firelauncher/.Launcher`，effective priority 仍為 50。
- Fire Launcher 在整個測量中未被修改。

### 已排除（此測試條件）

- 目前這個 PS7331 Accessibility/PendingIntent 組合不能被標記為可靠的
  Home-key redirect。
- 它沒有形成真正的 HOME replacement，也沒有改變 resolver state。

### 待驗證

- 服務若由研究者手動關閉後，兩個研究 APK 的移除 rollback 尚未在本次輸出中
  完成；這不是 HOME 結果的不確定性，而是裝置回復流程的人工前置條件。
- 其他明確不同的公開 Android API／使用者授權組合仍需個別測量，不能由本次
  0/20 結果推論所有輔助方案皆無效。

## 證據

公開、去識別化 artifact：
`artifacts/phase5cq/public-summary-20260805-01/`

原始 ADB、dumpsys、logcat 與逐迭代輸出保留在本機：
`adb/phase5/PHASE5CQ-ACCESSIBILITY-PENDINGINTENT-PS7331-T01/`

公開 artifact 包含：

- `summary.tsv`：20 次 foreground 結果。
- `resolver-before.txt` 與 `resolver-after.txt`。
- 篩選後的 `logcat-relevant.txt`。
- 原始輸入檔 SHA-256 map 與輸出 SHA-256 manifest。
- `metadata.json`：安全範圍與 rollback pending 狀態。

## 回復邊界

Accessibility service 必須由研究者在裝置 Settings 手動關閉，並關閉研究 App
中的 redirect toggle；之後才可執行既有 runner 的 `rollback` phase，移除兩個
研究 APK 並驗證 Fire Launcher resolver。未完成這個人工步驟前，本報告不宣稱
裝置已完成 rollback。

## 重現摘要

```sh
python3 tools/scripts/build_phase5cq_public_summary.py --dry-run \\
  --source adb/phase5/PHASE5CQ-ACCESSIBILITY-PENDINGINTENT-PS7331-T01 \\
  --output artifacts/phase5cq/public-summary-20260805-01
python3 tools/scripts/build_phase5cq_public_summary.py \\
  --source adb/phase5/PHASE5CQ-ACCESSIBILITY-PENDINGINTENT-PS7331-T01 \\
  --output artifacts/phase5cq/public-summary-20260805-01 \\
  --redirect-apk tools/phase4-accessibility/dist/20260804-keyevent-pendingintent-jdk17-01/org.fireosresearch.phase4.redirect.apk \\
  --alias-apk tools/test-launcher-phase4/dist/20260803-openjdk17-03/org.fireosresearch.phase4.alias.apk
(cd artifacts/phase5cq/public-summary-20260805-01 && shasum -a 256 -c sha256sums.txt)
```

本次結果是負向但有價值的 PS7331 runtime evidence：它縮小了「Accessibility
foreground redirect 可直接取代 HOME」這條路線，但沒有證明所有其他合法輔助
方案不可能，也沒有涉及 Root 或高風險系統修改。
