# Phase 5AH：HackMD／MTK 路徑與 exact KFTRWI 公開來源重查

## 結論摘要

本輪重新固定審查研究者提供的 HackMD、`mtk-easy-su`、`mtkclient` 與公開 exact-model 搜尋結果。

**已證實：** HackMD 主要描述 Qualcomm Adreno、Qualcomm ABL cmdline injection、Xiaomi `MIQSAS/IMQSNative` 與 Android isolated-service 鏈；它沒有提供 MediaTek MT8183、Amazon `trona` 或 `KFTRWI` 的 implementation。相關命令與服務不能送到本機作為「相近測試」。

**已證實：** 固定的 `mtk-easy-su` repository 仍是 legacy MTK wrapper，README 警告 2020-03 之後的 firmware 可能阻擋，tested-device table 沒有 `KFTRWI/trona/MT8183`；本機既有執行只到普通 app preflight，沒有 UID 0 證據。

**高可信推論：** 截至本輪公開搜尋，沒有可驗證的 `KFTRWI / trona / MT8183 / Android 9 / PS7330.4104N` root、bootloader unlock 或 custom-ROM implementation。這是有範圍的公開搜尋結論，不是對未公開漏洞的絕對否定。

**因風險拒絕測試：** Qualcomm-only exploit、Xiaomi-only Binder、未知 APK/native payload、generic MTK BROM/DA、seccfg／preloader／LK／partition write，以及把舊 Fire 8/9 代方法改名套用到 11 代。

## Exact device

| 欄位 | 值 | 既有證據 |
|---|---|---|
| Model | `KFTRWI` | `P5AF-DEVICE-001`; `adb/phase5/PHASE5AH-DEVICE-READONLY-20260804-01/props.stdout.txt` |
| Product | `trona` | `P5AF-DEVICE-001`; same read-only capture |
| SoC | MT8183 | `P5AF-DEVICE-001`; same read-only capture |
| Android | 9 / API 28 | `P5AF-DEVICE-001`; same read-only capture |
| Build | `PS7330.4104N/0030099376128` | `P5AF-DEVICE-001`; same read-only capture |
| Kernel | Linux 4.4.146+ | `P5AF-DEVICE-001`; `kernel_release.stdout.txt` |
| Patch | 2024-02-01 | `P5AF-DEVICE-001`; same read-only capture |
| Boot state | `flash.locked=1`, verified boot green | existing Phase 5 baseline |
| SELinux | Enforcing | current read-only check / P5AF |

Amazon 官方規格也將 2021 11th generation `KFTRWI` 列為 Fire OS 7、Android 9/API 28；這只確認產品邊界，不代表任何 MTK exploit 相容：[Amazon Fire Tablet specifications](https://developer.amazon.com/docs/device-specs/ft-device-specifications-firehd-models.html?v=firehd10_2023)。

## 1. HackMD 平台相容性

研究者提供的 [HackMD 漏洞列表](https://hackmd.io/@lokey0905/rk-hQSzibl) 所列主要鏈如下：

| HackMD 內容 | 真正平台／前提 | 與本機差異 | 判定 |
|---|---|---|---|
| CVE-2025-21479 | Qualcomm Adreno GPU micronode | 本機是 MediaTek MT8183，非 Adreno | 已排除 |
| ABL cmdline injection | Qualcomm ABL／fastboot OEM parser | 本機是 MTK boot chain；fastboot 已顯示 `locked hw` | 已排除 |
| `MIQSAS/IMQSNative` | Xiaomi 私有 system service | 本機是 Amazon Fire OS，沒有 Xiaomi service 證據 | 已排除 |
| Magica／isolated-service 後續鏈 | 特定 Android 版本、SELinux／seccomp 與 vendor service 前提 | 沒有 exact Fire PS7330 profile | 待驗證但不可直接執行 |

HackMD 自己也把內容定位為風險追蹤，並提醒需依 SoC、韌體與修補狀態驗證。它不是本機 MTK 操作手冊。為避免誤送 Qualcomm 指令，本輪沒有重現或執行其中的命令列注入／私有 Binder 範例。

## 2. `mtk-easy-su` implementation boundary

固定 revision：`8c6871ac7c15b8e98a47e25c35ab93b87e260475`。

公開 README 將它描述為以 Magisk 與 `mtk-su` 建立 bootless superuser access，並警告 2020-03 之後 firmware 可能阻擋；tested-device table 列出的平台是 MT6750、MT673x、MT8167、MT6771 等，沒有本機 exact target：[KoCleo/mtk-easy-su](https://github.com/KoCleo/mtk-easy-su)。

本專案已有 APK 靜態與 device observation：

- wrapper 會解出 `mtk-su32/64`、Magisk assets 與 shell script；
- shell script 需要成功的 temporary-root transition，之後才會走 permissive／Magisk／mount 類 privileged body；
- PS7330 測試只觀察到普通 app preflight，沒有 `uid=0`、`su -c id`、`getenforce=Permissive` 或成功 `/sbin/su` 證據；
- 因此不再重跑同一 APK，也不以改包裝、重命名或忽略 firmware warning 來製造「新測試」。

**已排除：** 這個 wrapper 本身不是 kernel exploit；它不能把其他 MTK 型號的 `mtk-su` payload 轉換成本機 PS7330 payload。

## 3. 公開 exact-model／near-target 搜尋

### Exact model

搜尋 `KFTRWI root GitHub`、`KFTRWI bootloader`、`trona MT8183 exploit`、`MT8183 Android 9 local privilege escalation` 與 Fire HD 10 11th-gen root／ROM 相關公開頁面，結果沒有找到可驗證的 exact `PS7330.4104N` root implementation。

找到的內容主要是：

- 舊 Fire 8／Fire HD 10 9th generation 的 amonet／bootless-root 歷史資料；
- 其他 MT8183 Chromebook 或 Android 13/14 裝置；
- 只有 `PS7330.4104N` 字串的普通 app／benchmark／使用者回報，沒有 exploit target、loader、offset 或 recovery set。

Amazon 官方產品頁確認本機是 11th generation；公開社群結果亦把已知 root 方法區分為較舊 Fire 世代，不能當作 exact PS7330 證據。[Amazon specs](https://developer.amazon.com/docs/device-specs/ft-device-specifications-firehd-models.html?v=firehd10_2023)

### MT8183 near-target

MT8183 Chromebook／mainline kernel source 可以作架構參考，但其 boot chain、device tree、firmware、Android container／ChromeOS policy 與 Amazon Fire OS 完全不同。搜尋到的 MT8183 公開 kernel／firmware內容沒有 `trona`、`KFTRWI`、PS7330 signed image 或 Amazon DA/auth profile。

**已證實（搜尋範圍內）：** SoC 相同不等於 preloader、DA、SLA/DAA、rollback、partition layout 或 signed kernel 相同。

## 4. BROM／fastboot 路徑目前狀態

既有安全 evidence 已記錄：

- `fastboot` 可識別 product `trona`；
- `getvar unlocked/secure/all` 回覆 `locked hw`；
- generic `mtkclient` source 有合併的 MT6771/MT8385/MT8183/MT8666 設定，但沒有 Amazon `trona` PS7330 loader／DA／auth 證明；
- PS7331 是相鄰版本，不能當作 PS7330 recovery 或 boot-chain compatibility proof。

**因風險拒絕測試：** 不執行 BROM handshake、DA upload、read/write、seccfg unlock、preloader/LK 寫入或 fastboot unlock。這些不是「可接受變磚」就能安全推導的測試；缺少 exact loader／DA／回復 image 時，結果可能是不可逆的 boot-chain state，而非可分析的 root log。

## 5. 公開 source evidence 對照

| Source | exact `KFTRWI/trona/PS7330` | Android／MTK implementation | 本輪動作 |
|---|---:|---|---|
| HackMD CVE list | 否 | Qualcomm／Xiaomi chains | 只讀平台 triage |
| `mtk-easy-su` pinned repo | 否 | legacy MTK wrapper + mtk-su payload | 使用既有 static/runtime evidence，不重跑 |
| generic `mtkclient` | 否 | BROM/DA/boot-chain tool | host-only source review |
| Fire 8/9 historical amonet | 否 | older Fire generation boot exploit | 不移植 |
| MT8183 Chromebook kernel | 否 | different firmware/boot/policy | 只作架構參考 |
| GhostLock Android ports | 否 | device/build-specific native kernel LPE | 不執行 |

## 6. 狀態標籤

### 已證實

1. 本機仍是 `KFTRWI/trona/MT8183/PS7330.4104N`、Android 9、4.4.146+。
2. HackMD 主要路徑不是 MTK/Amazon exact implementation。
3. `mtk-easy-su` 已在本機有失敗／無 UID 0 證據，且公開支援表不含本機。
4. 未找到公開 exact PS7330 root／bootloader implementation。

### 高可信推論

1. 目前最有價值的低層研究不是再跑 generic payload，而是取得完全匹配的 signed PS7330 boot/vmlinux／preloader metadata，做 host-only layout、patch 與 auth analysis。
2. 正式 HOME replacement 仍需 privileged/system-signed 或低層 boot-chain 能力；普通 ADB 與 Accessibility 不提供該能力。

### 待驗證

1. signed PS7330 kernel 是否 backport 過 GhostLock 修補。
2. Amazon 是否存在未公開的 exact PS7330 preloader／DA／recovery set。
3. PendingIntent Accessibility variant 在本機的實際前景成功率。

### 已排除

1. 直接套用 HackMD 的 Qualcomm 指令或 Xiaomi Binder。
2. 將舊 Fire 世代 root 方法套用到 11th-gen `trona`。
3. 將 MT8183 Chromebook 或其他 Android 版本的 exploit／boot image 當成本機 target。

### 因風險拒絕測試

未知 APK／native payload、kernel race、BROM/DA、preloader/LK、seccfg、fastboot unlock/write、boot image、partition、remount、SELinux policy 與任何需要 factory-reset 才能保證恢復的操作。

## 7. 下一個可執行研究入口

若要繼續，下一步只保留兩個有證據的方向：

1. **Host-only：** 取得與 PS7330.4104N 完全匹配的合法 signed artifact，核對 GhostLock backport、符號／layout 與 boot-chain metadata；沒有 artifact 就不產生 offset 或 live payload。
2. **Android user-authorized：** 只測量本專案自製 PendingIntent Accessibility variant，記錄前景成功率與延遲；不宣稱正式 HOME replacement。

本輪新建的唯讀裝置 capture 位於 `adb/phase5/PHASE5AH-DEVICE-READONLY-20260804-01/`；每個 stdout、stderr、exit code、command line 與 SHA-256 均保留。本輪沒有清理大型檔案：工作區仍有約 13 GiB 可用空間，且 `firmware/`、`decompiled/`、raw evidence 均屬專案原始資料，不應為了騰空間刪除。
