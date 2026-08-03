# Phase 5AE follow-up：最新 Android／MTK 公開實作與 exact target 審查

## 審查目的

本輪重新核對目前公開的 `KoCleo/mtk-easy-su`、研究者提供的 HackMD、
GhostLock（CVE-2026-43499）與 DirtyClone（CVE-2026-43503）資料，並與本機
`KFTRWI/trona/MT8183/Android 9/PS7330.4104N` 對照。只做公開來源與既有 exact-device
證據比對，沒有下載或執行第三方 root APK/native exploit，也沒有進入 boot chain。

## Exact device

| 欄位 | 值 | 證據 |
|---|---|---|
| Model / product | KFTRWI / trona | existing Phase 5 baseline |
| SoC | MediaTek MT8183 | existing Phase 5 baseline |
| Android | 9 / API 28 | existing Phase 5 baseline |
| Build | PS7330.4104N / Fire OS 7.3.3.0 | existing Phase 5 baseline |
| Kernel | Linux 4.4.146+ | existing Phase 5 baseline |
| Security patch | 2024-02-01 | existing Phase 5 baseline |
| SELinux | Enforcing | current read-only state |
| Verified Boot | green; `ro.boot.flash.locked=1` | existing read-only baseline |

## `mtk-easy-su` current revision

2026-08-04 重新查詢 GitHub remote：

```text
HEAD / refs/heads/master = 8c6871ac7c15b8e98a47e25c35ab93b87e260475
```

這與既有已封存的 source review 及 exact-device 測試使用的 commit 相同。該專案
仍是 Android wrapper + LFS `mtk-su32/64` payload；它不是可由 Android Studio
重新編譯出新 kernel exploit 的完整 source。既有 exact PS7330 測試已在 critical
init step 3 失敗，沒有 UID 0，因此本輪不重複。

公開 README 也明確提醒 2020 年 3 月後的 firmware 可能阻擋所用方法，且測試表沒有
KFTRWI、trona 或 MT8183。這與本機 PS7330 build 不構成 exact-target 支持。

**判定：已證實（公開版本範圍）：** 沒有發現新的 `mtk-easy-su` payload 或
KFTRWI/PS7330 profile；既有失敗 payload 不應再次執行。

## GhostLock 與 Android implementation

GhostLock 的核心是 Linux `rtmutex`／futex PI kernel path，不是 APK 或普通
PackageManager API。NebuSec 的公開文章目前描述的是 generic x86 Linux exploit chain，
並明確把 Android 的 reclaim、ASLR 與 CFI 適配列為後續工作；公開 Android port 也
各自綁定不同裝置與 kernel profile。

本機既有 source/config 證據只支持：

- MT8183 source family 有 FUTEX／RT_MUTEXES 及相關 proxy rollback path；
- Fire/MediaTek 4.4 source 與上游修補前語意相近；
- `task_struct`、kernel layout、KASLR、SELinux domain 與 signed PS7330 binary
  狀態尚未取得 binary-level 證明。

因此結論是：

- **已證實：** source/config family overlap。
- **高可信推論：** 其他 Android 6.12／5.10／MT6893／Snapdragon 的 target header、
  offset 或 native binary 不能直接套用到 MT8183/4.4。
- **待驗證：** signed PS7330 kernel 是否私下 backport，以及是否存在 exact
  `trona/PS7330` Android implementation。
- **因風險拒絕測試：** futex race、stack reclaim、kernel write、SELinux/root
  stage，以及錯配 profile 的 native payload。

## DirtyClone（CVE-2026-43503）

DirtyClone 是 Linux networking `skb` shared-fragment marker 問題，與 GhostLock
不是同一漏洞，也不是 Android HOME 或 MTK ION/CMDQ 路徑。既有 exact MT8183
defconfig 比對顯示其公開分析所依賴的 packet-duplication／TEE 入口缺少關鍵 config
選項；沒有 exact Android 4.4 PoC 或 PS7330 binary proof。

**判定：已排除（目前 scope）：** 把 DirtyClone 當成可直接套用的 Fire OS 7
temporary-root 路線，或重跑 generic Linux PoC。

## HackMD 路徑分類

研究者提供的 HackMD 內容列出的 Adreno micronode、Qualcomm ABL cmdline injection
及 Xiaomi `IMQSNative` 例子，依賴 Qualcomm GPU／ABL 或 Xiaomi 私有 service。這台
裝置是 Amazon MediaTek MT8183，沒有證據顯示存在這些元件、service 或 permission。

**判定：已排除：** Qualcomm/Xiaomi chain 作為 KFTRWI/PS7330 的 Android root
implementation。它可作漏洞分類參考，但不是本機測試候選。

## 現場狀態

- ADB：`device`。
- HOME resolver：`com.amazon.firelauncher/.Launcher`，effective priority 50。
- Accessibility：`services:{}`，尚未由研究者手動啟用。
- Phase 5AE 測試 APK：已安裝準備，但沒有自動啟用服務或 toggle。
- Fire Launcher：未停用、未隱藏、未 suspend、未 uninstall、未清除資料。

## 下一個有價值的最小步驟

1. 由研究者在 Settings 手動啟用 Phase 5AE Accessibility service，再測量公開
   `KEYCODE_HOME`／PendingIntent route；或
2. 取得可驗證且完全匹配 PS7330.4104N 的 signed boot/vmlinux，繼續做 host-only
   layout/patch analysis。

在上述條件出現前，沒有足夠證據支持把任何新 root payload 送入真機。重跑已知
`mtk-su64`、CMDQ v2 或其他裝置 GhostLock binary 不會增加 exact-target 證據。

## 公開來源

- [KoCleo/mtk-easy-su](https://github.com/KoCleo/mtk-easy-su)
- [Nebula Security：IonStack Part II](https://nebusec.ai/research/ionstack-part-2/)
- [GhostLock catalog](https://mallory.ai/vulnerabilities/CVE-2026-43499)
- [JFrog：DirtyClone](https://research.jfrog.com/post/dissecting-and-exploiting-linux-lpe-variant-dirtyclone-cve-2026-43503/)
- [研究者提供的 HackMD](https://hackmd.io/@lokey0905/rk-hQSzibl)
