# Phase 5AG：LauncherHijack Android 實作與 MT8183／PS7330 公開來源追查

## 研究範圍

本輪把「Android 的實作」分成兩個不應混用的問題：

1. Android 應用如何在不改變 HOME resolver 的前提下觀察 Home／Fire Launcher，並明確啟動另一個 Activity。
2. Linux／MediaTek CVE 的公開實作是否真的適用於本機 `KFTRWI / trona / MT8183 / PS7330.4104N`。

本輪以公開固定 revision、官方公告、既有 exact-device capture 與本地 source 為依據。沒有下載、編譯或執行第三方 exploit／PoC；沒有開啟 device node、呼叫 ioctl、觸發 kernel race、執行 BROM／DA、fastboot 或任何分割區操作。既有原始 capture 不覆寫。

## Exact device boundary

| 欄位 | 值 | 證據 |
|---|---|---|
| Device | Amazon Fire HD 10 11th Gen / KFTRWI | `P5AF-DEVICE-001` |
| Product / SoC | `trona` / MediaTek MT8183 | `P5AF-DEVICE-001` |
| Android | 9 / API 28 | `P5AF-DEVICE-001` |
| Build | `PS7330.4104N/0030099376128` | `P5AF-DEVICE-001` |
| Security patch | `2024-02-01` | `P5AF-DEVICE-001` |
| Kernel | Linux `4.4.146+` | `P5AF-DEVICE-001` |
| HOME | `com.amazon.firelauncher/.Launcher`, effective priority 50 | `P5AF-DEVICE-005` |
| ADB caller | UID 2000 / `u:r:shell:s0` | `P5AF-DEVICE-001` |

既有 raw capture 位於 [`adb/phase5/PHASE5AF-ANDROID-CVE-SURFACE-20260804-02/`](../adb/phase5/PHASE5AF-ANDROID-CVE-SURFACE-20260804-02/)。本輪沒有新增裝置端變更，因此 HOME、Accessibility、package state 與 ADB 狀態沿用該 capture；這不是重新測試。

## A. LauncherHijack 的 Android 實作

審查固定 commit [`f79aee3ddd10c053d6d7c55d6f2fc29436001537`](https://github.com/BaronKiko/LauncherHijack/tree/f79aee3ddd10c053d6d7c55d6f2fc29436001537)，避免使用會漂移的 branch。

### A.1 目標 Intent 與啟動邊界

固定版 [`HomePress.java`](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/app/src/main/java/com/baronkiko/launcherhijack/HomePress.java) 的 `GetDesiredIntent()`：

- 從自己的 `SharedPreferences` 讀取目標 package／class。
- 建立 `Intent.ACTION_MAIN`。
- 加入 `Intent.CATEGORY_LAUNCHER`，不是 `CATEGORY_HOME`。
- 指定 explicit `ComponentName`。
- 加入 `NEW_TASK | EXCLUDE_FROM_RECENTS | CLEAR_TOP | REORDER_TO_FRONT`。

`Perform()` 再以 `PendingIntent.getActivity(...).send()` 發送這個 explicit intent。這條路徑不要求 PackageManager 重新選 HOME，也不寫 ordinary preferred activity；它只是讓應用在事件發生後嘗試把指定 Activity 帶到前景。

**已證實：** 這是 foreground redirect，不是正式 HOME replacement。

### A.2 事件來源

固定版 [`AccServ.java`](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/app/src/main/java/com/baronkiko/launcherhijack/AccServ.java) 有三個觀察入口：

| 入口 | 實作 | 意義 |
|---|---|---|
| `onAccessibilityEvent` | 看到 `com.amazon.firelauncher` 後呼叫 `HomePress.Perform()` | 先讓 Fire Launcher 成為可觀察的前景，再顯式啟動目標 |
| `onKeyEvent` | 在使用者啟用 hardware detection 時處理 `KEYCODE_HOME` | 依公開 Accessibility API 攔截／回傳 key event |
| `HomeWatcher` | 觀察 `ACTION_CLOSE_SYSTEM_DIALOGS` 的 home/recent reason | 事件觀察，不是 system_server callback |

**高可信推論：** 這種實作可能改變使用者看到的前景 Activity，但無法使 `cmd package resolve-activity`、`mAlways` preferred record 或 Fire Launcher protected state 改變。

### A.3 與本專案 variant 的關係

本專案的 `tools/phase4-accessibility` variant 刻意只使用人工啟用的 Accessibility、可見 toggle、package filter、cooldown 與 loop guard；不宣告 device-admin、私有 Binder、network 或修改 Fire Launcher state。

既有直接 `startActivity()` 路徑的 `PHASE4-ACCESSIBILITY-T03` 是 0/30 成功前景 handoff；這個結果只排除該實作與當時條件，不排除所有可能的 Android foreground API。PendingIntent variant 尚無新的裝置測量，仍標為**待驗證**，不能宣稱可用。

### A.4 歷史「腐化預設 Launcher」路徑

固定版文件 [`HELP.md`](https://raw.githubusercontent.com/BaronKiko/LauncherHijack/f79aee3ddd10c053d6d7c55d6f2fc29436001537/HELP.md) 另記載一條舊 Fire OS 的「Disable the Default Launcher」做法，文件本身警告可能腐化 default launcher；若沒有可用的第三方 Launcher，裝置可能難以操作，且問題可能只對目前 user account 有效，需要新 user account 才能恢復。

這不是單純的 Accessibility redirect，也不是可在 PS7330 上安全推論的 Android API。來源文件未提供本機 exact build、package signature 或恢復保證。

**因風險拒絕測試：** 不下載、不安裝、不模擬該未知腐化 APK；不以它改寫 Fire Launcher／HOME state。原因是可能留下無 HOME、user-level default corruption 或需新 user／factory reset 的恢復條件。

官方 repository 也標示 deprecated，並指出 Amazon 已將其 package name 加入 FireOS blocked app list，且某些「hacky」方法可能因小版本變化失效：[固定版 README](https://github.com/BaronKiko/LauncherHijack/tree/f79aee3ddd10c053d6d7c55d6f2fc29436001537)。

## B. CVE 編號與 Android／Linux 實作邊界

### B.1 `CVE-2026-3499` 不屬於 Android kernel

NVD 將 `CVE-2026-3499` 記錄為 WordPress Product Feed PRO for WooCommerce 的 CSRF，不是 GhostLock，也不是 Linux／Android kernel 漏洞：[NVD record](https://nvd.nist.gov/vuln/detail/CVE-2026-3499)。

**已排除：** 不能以此 CVE 作為本機 kernel root 或 boot image 分析目標。

### B.2 GhostLock 的 Android 實作層

GhostLock 對應 `CVE-2026-43499`。其 Android 入口若存在，屬於普通 native process → Bionic／syscall → kernel futex/rtmutex 路徑；後續 root chain 還需要依 exact kernel build 調整 layout、地址／leak、架構、SELinux 與 credential stage。它不是一般 APK 權限或 Android Framework API。

公開研究索引中的 Android target 是裝置／build 專用；例如公開索引描述了 Samsung、OnePlus、OPPO 等不同 kernel／firmware profile，沒有 `KFTRWI/trona/MT8183/PS7330.4104N` profile：[Mallory GhostLock index](https://mallory.ai/vulnerabilities/CVE-2026-43499)。

本機既有 source/config 只支持 `CONFIG_FUTEX=y`、`CONFIG_RT_MUTEXES=y` 與修補前 code family overlap；它不證明 signed PS7330 binary 未 backport，也不產生可安全執行的 target offsets。

**判定：**

- **已證實：** Android implementation 的核心層是 native syscall 與 kernel futex/rtmutex，不是 APK resolver。
- **高可信推論：** 其他 Android 5.10/6.12、不同 SoC 或不同 build 的 offset／target header 不能直接套用到本機 4.4.146。
- **待驗證：** signed PS7330 kernel 的實際 backport、layout 與 exact exploitability；目前沒有可驗證 binary-level exploit target。
- **因風險拒絕測試：** futex race、UAF reclaim、kernel memory write、SELinux／credential stage、未知 native payload。

### B.3 DirtyClone 的 Android 實作層

`CVE-2026-43503` 是不同的 Linux `net/skbuff`／XFRM／ESP frag-transfer 路徑。公開 source 是 Linux C reproducer，不是 Android APK，也沒有本機 target profile：[0xBlackash reproducer](https://github.com/0xBlackash/CVE-2026-43503)、[rafaeldtinoco research tree](https://github.com/rafaeldtinoco/security/tree/main/exploits/dirtyclone)、[JFrog analysis](https://research.jfrog.com/post/dissecting-and-exploiting-linux-lpe-variant-dirtyclone-cve-2026-43503/)。

本機 `P5AF-DEVICE-001`／既有 exact source capture 的相關觀察：

| 前提 | 本機觀察 | 判定 |
|---|---|---|
| user namespace sysctl | 兩個 desktop PoC 常用 sysctl 不存在 | 公開 PoC 前提未形成 |
| `xt_TEE` / ESP / XFRM modules | 未見 runtime module surface | 公開 PoC 路徑不相符 |
| `/proc/net/xfrm_stat` | 不存在 | 未見可用 XFRM stats endpoint |
| exact defconfig | `NF_DUP_IPV4=n`、`NF_DUP_IPV6=n`、`NETFILTER_XT_TARGET_TEE=n`、`NF_TABLES=n` | 主要 documented TEE/duplicate entry 不相符 |

**已排除（目前 documented route）：** DirtyClone 公開 Linux PoC 不是本機 Android 9 的可驗證 exact root 路徑。這不是對所有未公開 network bug 的絕對否定。

## C. 官方 MediaTek bulletin 篩選

這裡只作 source／target triage，不把「同一 SoC」誤當成「同一 Android build」。官方公告中的 affected software version、chipset list 與本機 Android 9／PS7330 必須同時匹配。

| CVE | 層級／影響 | MT8183 | 公告 software scope | 本機 exact fit | 判定 |
|---|---|---:|---|---|---|
| CVE-2025-20694 | Bluetooth buffer underflow；DoS | 是 | Android 13/14/15 | Android 9；影響也不是 local root | 已排除為本機 root 路徑 |
| CVE-2025-20696 | DA OOB write；需 physical access／user interaction，可能 LPE | 否 | Android 13/14/15 等 | SoC、OS、入口均不匹配 | 已排除 |
| CVE-2025-20697 | Power HAL OOB write；需先有 System privilege | 否 | Android 14/15 | 無 MT8183，且非 shell-to-system 起點 | 已排除 |
| CVE-2025-20698 | Power HAL OOB write；需先有 System privilege | 否 | Android 13/14/15 | 無 MT8183，且非 shell-to-system 起點 | 已排除 |
| 2026 MediaTek bulletin rows reviewed | modem／telephony／新 Android scope | 未找到 exact `MT8183 + Android 9 + local shell` row | 依各公告 | 未形成 exact route | 待驗證；不是可執行候選 |

官方公告：[MediaTek July 2025 bulletin](https://corp.mediatek.com/product-security-bulletin/July-2025)、[MediaTek August 2025 bulletin](https://corp.mediatek.com/product-security-bulletin/August-2025)。July 2025 公告中的 MT8183 命中是 CVE-2025-20694，但其 Android 版本與影響類型不符合本機 root 目標；August 2025 的 CVE-2025-20696 affected chipset list 不含 MT8183，且是 DA／physical-access 路徑。

**高可信推論：** 目前公開 MediaTek bulletin 沒有提供可直接套用到 PS7330 的 Android 9 shell-to-root 實作。

## D. 公開 Android implementation 對照

| 參考 | Android 實作類型 | Exact PS7330 | 本輪處置 |
|---|---|---:|---|
| LauncherHijack fixed commit | Accessibility／system-dialog observation → explicit Activity → PendingIntent | 否；本專案 direct-start 舊路徑 0/30 | 只作 source review；未新增裝置變更 |
| 本專案 PendingIntent variant | 公開 Accessibility + explicit `CATEGORY_LAUNCHER` | 尚未測量 | 保留為低風險待驗證，不宣稱成功 |
| GhostLock Android ports | native futex/rtmutex kernel LPE，device/build offsets | 否 | 不下載、不執行 |
| DirtyClone GitHub C | Linux networking reproducer | 否 | 不在 Android 執行 |
| `KoCleo/mtk-easy-su` | legacy MTK wrapper + bundled payload | 否；固定 payload 已在本機失敗 | 不重跑；不以 APK wrapper 掩蓋 target mismatch |
| generic `mtkclient` | BROM／DA／boot-chain workflow | 否；缺 matching loader/DA/auth evidence | 因 boot-chain 風險拒絕 |

`mtk-easy-su` 公開說明也列出其支援裝置主要是較舊 MTK 平台，並警告 2020 年後 firmware 可能阻擋；它不是本機 PS7330 的 exact implementation：[KoCleo/mtk-easy-su](https://github.com/KoCleo/mtk-easy-su)。

## E. 目前可做與不可做的結論

### 已證實

1. LauncherHijack 的 Android code 是 event observer + explicit launcher Activity + PendingIntent；不會改變正式 HOME resolver。
2. `CVE-2026-3499` 與 Android kernel 無關。
3. `CVE-2026-43499`／GhostLock 與 `CVE-2026-43503`／DirtyClone 是不同 kernel subsystem，不能交叉套用。
4. 目前公開 MediaTek rows 沒有同時符合本機 `MT8183 + Android 9 + PS7330` 的已知 local shell-to-root implementation。

### 高可信推論

1. 若只允許無 Root、不可停用 Fire Launcher、不可改分割區，最接近可測的 Android 路徑仍是需研究者明確授權的 Accessibility foreground redirect；它不是正式 HOME replacement。
2. 對 GhostLock 而言，先取得 exact signed kernel／boot artifact 做 host-only patch/layout review，比盲目執行別的手機 offset 或 kernel race 更有研究價值。

### 待驗證

1. PendingIntent variant 在本機 Fire OS 7 上的實際前景成功率、延遲與閃現情況。
2. signed PS7330 kernel 是否已 backport GhostLock 修補，以及是否存在可公開驗證的 exact target metadata。
3. 2026 MediaTek 公告中未明列的其他 MT8183 firmware issue 是否與本機 Android 9 相關；目前沒有 exact local-root 證據。

### 已排除

1. 以 priority APK、普通 `set-home-activity` 或歷史 LauncherHijack redirect 宣稱正式 HOME replacement。
2. 將 DirtyClone Linux C reproducer 當成 Android 9／MT8183 root APK。
3. 將 `CVE-2026-3499` 當 GhostLock。
4. 將其他 Android build 的 GhostLock target offset、generic MTK tool 或未知 APK 直接套用成本機。

### 因風險拒絕測試

未知 root APK／native payload、futex race、kernel memory write、AEE／ION／CMDQ ioctl、BROM／DA handshake、preloader／LK／seccfg、fastboot unlock／write、boot image 或分割區修改，以及歷史「腐化 default launcher」APK。這些目前缺 exact target 或可能要求不可逆恢復，不能因研究者願意承擔設備損壞就直接執行。

## F. 最小後續路徑

1. 若要繼續 Android 方向，只做一次已明確授權的 PendingIntent variant foreground measurement；保存原始 Accessibility state，結束時由研究者關閉 service／toggle 並移除自製 APK。
2. 若要繼續 kernel 方向，先取得合法、與 `PS7330.4104N` 完全匹配的 boot／vmlinux／符號或 vendor artifact，僅做 host-only source／layout／patch comparison；沒有 exact artifact 就不進入 live exploit。
3. 不再投入 priority 矩陣、普通 preferred record、已失敗 mtk-su、DirtyClone network prerequisite 或 generic BROM tool。

## Reproduction

本輪 source review 的固定資料與判定矩陣：

```sh
python3 tools/scripts/validate_phase5ag_review.py \
  --matrix output/tables/phase5ag-mtk-bulletin-matrix.csv \
  --source-manifest artifacts/phase5/launcherhijack-and-mtk-bulletin-followup-20260804-01/source-manifest.csv
```

只讀查看既有 exact capture：

```sh
sed -n '1,220p' findings/phase-5af-android-cve-and-poc-review.md
sha256sum adb/phase5/PHASE5AF-ANDROID-CVE-SURFACE-20260804-02/sha256sums.txt
```

本輪沒有新增裝置命令；來源未下載，source manifest 的 `sha256` 欄位因此明確標為 `NOT_DOWNLOADED`，不冒充原始檔雜湊。
