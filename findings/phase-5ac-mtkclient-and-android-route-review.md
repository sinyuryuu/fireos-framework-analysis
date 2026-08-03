# Phase 5AC：MTKClient 相容性與 Android 測試路徑

## 本輪結果

本輪完成兩項可驗證進展：

1. 固定目前公開 mtkclient source，確認 MT8183 被列在共享的
   MT6771/MT8385/MT8183/MT8666 profile，該 profile 的 dacode 是 0x6771；
   source 中沒有獨立 0x8183 key。
2. 將 Phase 5AB PendingIntent Android variant 編譯成 Android 9 可安裝 APK，
   並完成裝置上的 before snapshot 與安全安裝準備。Accessibility 仍未由 ADB
   開啟，等待研究者在 Settings 明確同意。

這兩項都不是 root 或 bootloader 成功證據。

## Exact device

| 欄位 | 值 |
|---|---|
| Serial | G001LT0511550CFT |
| Device | KFTRWI / trona |
| SoC | MediaTek MT8183 |
| Build | PS7330.4104N/0030099376128 |
| Android | 9 / API 28 |
| Kernel | 4.4.146+ |
| Verified boot | green |
| Flash state | locked |
| HOME | com.amazon.firelauncher/.Launcher, priority 50 |

## Android APK implementation

### Build evidence

自建 APK：

| 項目 | 值 |
|---|---|
| Package | org.fireosresearch.phase4.redirect |
| APK SHA-256 | 9e8c38f51ca84bd6e8b6015d4d9b02920a548c1470a938dd41b3be857c3b2f28 |
| Min / target SDK | 28 / 28 |
| Signature | v3 verified |
| Build tool | Android API 35 / build-tools 35.0.0 |
| JDK | OpenJDK 17.0.20 |
| Network permission | none |
| Accessibility consent | not automated |

### Device preparation T01

adb/phase5/PHASE5AB-PENDINGINTENT-T01/ 保存：

- 完整 before snapshot；
- redirect APK 與 alias APK SHA-256；
- install stdout/stderr/exit code；
- Accessibility after-install dump；
- package paths；
- resolver state；
- preparation SHA-256 manifest。

Observed after installation:

- 兩個研究 APK 已安裝；
- dumpsys accessibility 的 services 仍為空；
- HOME resolver 仍是 com.amazon.firelauncher/.Launcher；
- Fire Launcher 沒有被停用、隱藏、suspend、force-stop、卸載或清除資料；
- 沒有寫入 Settings、AppOps、preferred activity、overlay 或 DeviceConfig。

**已證實：** 安全安裝沒有改變正式 HOME resolver。

### 尚待手動完成

必須由研究者在裝置 Settings：

1. 打開控制頁的 Redirect enabled；
2. 手動啟用 Phase 4 redirect Accessibility service；
3. 回到測試頁。

之後才可以使用 measure phase；本系統不會透過 ADB 自動寫入
enabled_accessibility_services。因此現在不能把 T01 稱為 redirect 成功或失敗。

## MTKClient public source review

固定 revision：

0542a8729993000661e2325e838217ee754d1632

source-level facts:

- brom_config.py 有共享名稱 MT6771/MT8385/MT8183/MT8666；
- 同一 profile 使用 dacode=0x6771 與 mt6771_payload.bin；
- 沒有獨立 0x8183 config key；
- 0x8168 是另一個 MT8168/MT6357 profile，不能當作 MT8183；
- README 的 BROM、preloader、DA、root、read/write/erase 說明屬於 boot-chain
  操作，不是 Android shell API。

**高可信推論：** mtkclient 可能在某些 MT8183 bootrom family 上具備程式碼層
識別或實驗支援；但這不足以證明 Amazon trona 的 preloader、DA、
SLA/DAA、SBC、rollback 或 seccfg chain 相容。

目前 exact evidence 仍是：

- ro.boot.flash.locked=1；
- current workspace 只保存相鄰 PS7331 boot-chain artifacts，標記為
  VERSION_MISMATCH；
- 沒有 exact PS7330 preloader/LK/DA/auth bundle；
- 沒有安全的恢復 image 與分割區回滾證據。

因此不執行 mtkclient 的 BROM、payload、crash、preloader、DA、seccfg、
read/write/erase、fastboot 或 flash 路徑。

## MTK route matrix

機器可重現輸出：

output/tables/phase5ac-mtkclient-android-route-matrix.csv

生成器：

~~~sh
python3 tools/scripts/analyze_phase5ac_mtkclient_compat.py \
  --config-excerpt artifacts/phase5/mtkclient-android-route-review-20260804-01/brom-config-excerpt.txt \
  --device-report findings/phase-5r-mtk-root-route-review.md \
  --test-metadata adb/phase5/PHASE5AB-PENDINGINTENT-T01/metadata.tsv \
  --output output/tables/phase5ac-mtkclient-android-route-matrix.csv
~~~

dry-run 只讀本地輸入，不呼叫 ADB、網路或 mtkclient。

## 安全邊界與拒絕項

**已排除：**

- 重跑固定 mtk-su64；其 exact PS7330 step-3 failure 已有證據；
- 把 shared 0x6771 profile 當成 exact Amazon loader；
- 把 PS7331 image 當成 PS7330 boot-chain artifact；
- 把 Android APK wrapper 當成 kernel exploit compatibility；
- 把 PendingIntent redirect 當成 HOME resolver replacement。

**因風險拒絕測試：**

- BROM exploit、preloader payload、DA upload；
- seccfg unlock、userdata/metadata erase；
- boot/vbmeta/preloader/LK/system/vendor/product 寫入；
- fastboot unlock/flash；
- CMDQ/ION/AEE/futex 新 trigger 或 ioctl；
- 未知 Binder、SELinux 修改、remount。

## 當前最接近的可測試路徑

低風險路徑是 PendingIntent redirect：它只可能形成前景替代，不會改變正式
HOME。當前 T01 已準備完成，等待手動 Accessibility consent；成功與否必須由
mResumedActivity、mCurrentFocus、延遲、閃現與 rollback 證據決定。

低層 root 路徑目前沒有新的 exact-target payload。公開 mtkclient 文檔明確涵蓋
BROM、root、flash 與 erase 操作，但這些公開命令不提供 Amazon-specific
preloader/auth/recovery 證明；相關 live 操作保持拒絕。

## 證據級別

- **已證實：** APK build/signature/hash、T01 安裝與 snapshot、Fire HOME 未變。
- **高可信推論：** shared MT6771 profile 不能單獨證明 Amazon MT8183 相容。
- **待驗證：** PendingIntent foreground handoff；exact signed PS7330 boot-chain
  private state。
- **因風險拒絕測試：** MTKClient boot-chain 與 kernel-memory live routes。

## Sources

- [mtkclient fixed source](https://github.com/bkerler/mtkclient/tree/0542a8729993000661e2325e838217ee754d1632)
- [mtkclient brom_config.py](https://raw.githubusercontent.com/bkerler/mtkclient/0542a8729993000661e2325e838217ee754d1632/mtkclient/config/brom_config.py)
- [mtkclient README-USAGE.md](https://github.com/bkerler/mtkclient/blob/0542a8729993000661e2325e838217ee754d1632/README-USAGE.md)
- [KoCleo/mtk-easy-su fixed source](https://github.com/KoCleo/mtk-easy-su/tree/8c6871ac7c15b8e98a47e25c35ab93b87e260475)
