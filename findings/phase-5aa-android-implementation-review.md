# Phase 5AA：公開 Android 實作與 exact PS7330 相容性重查

## 目的與安全範圍

本輪針對「公開 kernel/Android PoC 是否有可參考的 Android 實作」做主機端、來源
固定版本的審查。目標裝置是研究者擁有的 Amazon Fire HD 10 2021（`KFTRWI` /
`trona`），不是把公開 payload 移植或執行到裝置上。

本輪只讀取公開 repository 的 metadata、README、Android wrapper source、Git-LFS
pointer 與既有本地證據；沒有下載或執行 APK、native library、root payload、BROM/DA
或 preloader，也沒有發送 ioctl、開啟新的 device node、重開機、修改套件或寫入任何
分割區。原始未追蹤的使用者資料未修改。

## Exact device baseline

| 欄位 | 已保存值 | 證據 |
|---|---|---|
| Model / product | `KFTRWI` / `trona` | `findings/phase-5m-evidence-index.md`，`P5M-BASE-001` |
| SoC | MediaTek `MT8183` | `P5M-BASE-001` |
| Android / API | Android 9 / API 28 | `P5M-BASE-001` |
| Build | `PS7330.4104N` | `P5M-BASE-001` |
| Security patch | `2024-02-01` | `P5M-BASE-001` |
| Kernel | Linux `4.4.146+` | `P5M-BASE-001` |
| Verified Boot / SELinux | green / Enforcing | `P5M-BASE-001` |
| shell caller | UID 2000、`u:r:shell:s0` | `P5M-BASE-001` |
| exact mtk-su result | pinned `mtk-su64` 執行失敗；exit 1、`Failed critical init step 3`，沒有 UID 0 | `P5E-CMDQ-007` |

## Android implementation 不是單一層

公開專案中的「Android 實作」可分成四種，不能只看到 APK 就視為 Android
framework 漏洞：

```text
Kotlin/Java UI or wrapper
        │
        ├─ ordinary Android API / Runtime.exec / dynamic-loader boundary
        │
        ├─ native ABI code (futex, pipe, driver ioctl, or detector)
        │
        ├─ Linux kernel implementation (rtmutex, pipe, driver)
        │
        └─ preloader / LK / secure boot chain (Android userspace 尚未啟動)
```

### `mtk-easy-su` 的實際 Android 邊界

固定版本 `KoCleo/mtk-easy-su`（`8c6871ac7c15b8e98a47e25c35ab93b87e260475`）的
Android source 是 wrapper，不是 MTK exploit 的完整 source：

1. `AndroidManifest.xml` 只宣告 `INTERNET` 與 `RECEIVE_BOOT_COMPLETED`，沒有使
   一般 APK 變成 privileged/system app 的權限。
2. `MainActivity` 讀取安全修補日期、顯示警告，按鈕觸發 `ExploitHandler`。
3. `ExploitHandler` 從 assets 解出 32/64 位檔案、設定 executable mode、執行 bundled
   shell/Magisk 流程，最後以 `/sbin/su` 是否存在作為粗略成功訊號。
4. `mtk-su32`、`mtk-su64` 與 `magisk-boot.sh` 在該 commit 是 Git-LFS pointer；
   Android repository 內沒有可針對 `MT8183/PS7330` 重新編譯的 payload source。
5. 其中 `mtk-su64` 的 LFS object ID 與先前在本機測試的 binary 相同；因此不能把
   「GitHub 上仍有 Android APK」誤報為新的測試路線。

**判定：已證實。** 這個 project 的 Android 部分可用來理解 wrapper 行為，但目前
固定 payload 在 exact PS7330 上已失敗；不重跑等價 payload。

## 公開 CVE-2026-43499 Android 實作對照

| 公開專案 | Android 實作 | 公開 target | 與 KFTRWI/PS7330 的差異 | 判定 |
|---|---|---|---|---|
| `x-spy/CVE-2026-43499-popsicle` | arm64 native preload，依 boot/XBL 與 target 生成器產生裝置資料 | Xiaomi 17、Snapdragon、Android 16、kernel 6.12.23 | SoC、Android、kernel generation、boot artifact 全不同 | **已排除：不可直接移植** |
| `Linuxoid-cn/CVE-2026-43499-Poc-Analysis` | generic Android arm64 target/profile framework | Xiaomi-oriented；要求 exact boot/profile | 沒有 `trona`/`MT8183`/`PS7330` profile | **高可信推論：只能作方法參考** |
| `soralis0912/CVE-2026-43499-aristotle` | MediaTek native port；重新推導 5.10 layout、anchors 與 target | Xiaomi XIG04、Android 12、kernel 5.10.136 | 本機是 Android 9、4.4.146+；README 也明示尚未硬體驗證 | **已排除：不是 exact target** |
| `CakesTwix/Android-CVE-2026-43499` | Kotlin detector + ABI-specific native test；以 process termination 行為判定 | Android 7+ ARM，detector | 沒有 exact PS7330 驗證；README 警告可能 crash/reboot | **因風險拒絕安裝／執行** |
| `NebuSec/CyberMeowfia` | Linux/native source family；Android 需另行 target port | 多種 Linux/Android 研究 target | 沒有 exact `trona` Android target；文章本身不等於 Fire port | **待驗證：僅 source 參考** |

最重要的 Android porting 結論是：即使同一個 CVE，`target.h`、kernel layout、物理
載入位置、KASLR/stack 假設與 Android ABI 仍會隨每個 device/build 改變。XIG04
的 MediaTek port 並沒有證明 4.4.146 的 MT8183 可以使用同一組資料。

## 其他 Android／MTK 候選

### Dirty Pipe

`polygraphene/DirtyPipe-Android` README 將支援範圍限定在 Pixel 6 的
2022-02-05 至 2022-04-05 security patch，並明確警告可能 crash/reboot 或造成
brick。目標裝置的 kernel 是 4.4.146+、patch 是 2024-02-01；這是 kernel generation
與版本邊界不一致，不是可直接用的 Android implementation。`tiann/DirtyPipeRoot`
也只是 temporary-root wrapper，不能補上這個 target mismatch。

**判定：已排除（版本／裝置不符）；不安裝。**

### Qualcomm、Xiaomi service 與 Magica

使用者提供的 HackMD 將 Qualcomm Adreno、Qualcomm ABL、Xiaomi `IMQSNative` /
`MQSAS` 與 isolated-service 類鏈列在同一份清單中；這些是不同 OEM/SoC/SELinux
前提的實作。KFTRWI 是 MediaTek MT8183，沒有證據顯示它有 Qualcomm ABL 或 Xiaomi
MQSAS service。不能因它們都能在「Android」上出現，就當成同一條 Android root API。

**判定：已證實為 scope mismatch；不改寫 fastboot/SELinux，不呼叫未知 binder。**

### fenrir 與 OPlus preloader project

`fenrir`、`oppo-mtk-fastboot-unlock` 的實作在 preloader/secure-boot chain，
Android userspace 啟動以前；其 loader、DA/auth、OEM image、rollback 與 recovery
條件都不是 Amazon `trona` 的證據。這些不是「下載 APK 後可測的 Android 實作」。

**判定：高可信推論／Level 3 路線；拒絕 BROM/DA、preloader、LK、fastboot 或 image
write。**

## Exact-device compatibility matrix

可重現輸出：

- `output/tables/phase5aa-android-implementation-matrix.csv`
- `artifacts/phase5/android-implementation-public-review-20260804-01/`
- 產生器：`tools/scripts/analyze_phase5aa_android_implementations.py`

產生器只讀取保存的報告與 metadata，支援：

```sh
python3 tools/scripts/analyze_phase5aa_android_implementations.py --dry-run \\
  --device-report findings/phase-5m-evidence-index.md \\
  --existing-review findings/phase-5x-android-implementation-and-route-review.md \\
  --source-metadata artifacts/phase5/android-implementation-public-review-20260804-01/repo-metadata.tsv \\
  --output output/tables/phase5aa-derived
```

live mode 只會寫 host output，不會連接裝置；輸出目錄已存在時會拒絕覆寫。

## 分級結論

### 已證實

- exact device 是 `KFTRWI/trona/MT8183/Android 9/PS7330.4104N`，而不是公開 Android
  port 所使用的 Xiaomi、Pixel、Samsung 或 OPlus target。
- `mtk-easy-su` 的 Android source 是 wrapper，且 pinned `mtk-su64` 已有 exact
  PS7330 失敗證據。
- `aristotle` 提供了「依 exact kernel/build 重新生成 Android native target」的
  方法學證據，但沒有提供本機 target。
- Dirty Pipe、Qualcomm、Xiaomi service、fenrir 與 OPlus preloader 路線各自落在
  不同版本、SoC 或 boot-chain 邊界。

### 高可信推論

- 若要繼續研究 GhostLock，真正缺的是 exact signed PS7330 kernel/boot artifact
  與完整編譯布局，而不是另一個通用 Android wrapper。
- `MT8183` 這個 SoC 名稱本身不足以支持任何 Android root payload；必須同時匹配
  kernel、OEM backport、build、layout、ABI、SELinux 與 recovery path。

### 待驗證

- signed PS7330 kernel binary 是否對 GhostLock 做了私有 backport；目前只有 source
  family/config overlap，沒有 signed binary proof。
- 未來是否會出現公開的 `trona/MT8183/PS7330` Android target；本輪只代表固定
  repository set 的搜尋結果。

### 已排除

- 將 `CVE-2026-43503` 當作 GhostLock Android implementation。
- 將 `CVE-2026-3499` 當成已識別的 Android root CVE。
- 把 `popsicle`、`aristotle`、Pixel Dirty Pipe、Samsung/OPlus installer 或
  `mtk-easy-su` 的新下載視為 exact PS7330 payload。

### 因風險拒絕測試

- detector/native trigger、futex race、AEE race、ION/CMDQ 新 ioctl、未知 binder、
  BROM/DA handshake、preloader/LK 修改、fastboot unlock、remount、分割區寫入。

## 下一個合理目標

1. 若能取得有可信來源且與 `PS7330.4104N` 完全匹配的 signed boot/kernel artifact，
   僅做 offline symbol、config、`rtmutex`/`futex` backport 與 Android ABI 比對。
2. 若拿不到 exact artifact，保留現有 source/config evidence，將公開 Android
   implementation 搜尋標記為完成；不要再用其他裝置的 payload 做猜測性測試。

目前沒有足夠證據支持新的 Android APK、無 Root ADB 路線或 exact PS7330 temporary
root。這是可重現性與安全邊界結論，不是對所有未公開漏洞的絕對否定。

## References

- [KoCleo/mtk-easy-su pinned source](https://github.com/KoCleo/mtk-easy-su/tree/8c6871ac7c15b8e98a47e25c35ab93b87e260475)
- [mtk-easy-su `ExploitHandler.kt`](https://github.com/KoCleo/mtk-easy-su/blob/8c6871ac7c15b8e98a47e25c35ab93b87e260475/app/src/main/java/juniojsv/mtk/easy/su/ExploitHandler.kt)
- [x-spy/CVE-2026-43499-popsicle](https://github.com/x-spy/CVE-2026-43499-popsicle)
- [Linuxoid-cn/CVE-2026-43499-Poc-Analysis](https://github.com/Linuxoid-cn/CVE-2026-43499-Poc-Analysis)
- [soralis0912/CVE-2026-43499-aristotle](https://github.com/soralis0912/CVE-2026-43499-aristotle)
- [CakesTwix Android detector](https://github.com/CakesTwix/Android-CVE-2026-43499)
- [polygraphene DirtyPipe Android](https://github.com/polygraphene/DirtyPipe-Android)
- [R0rt1z2/fenrir](https://github.com/R0rt1z2/fenrir)
- [Shocked-Cat/oppo-mtk-fastboot-unlock](https://github.com/Shocked-Cat/oppo-mtk-fastboot-unlock)
- [NebuSec IonStack Part II](https://nebusec.ai/research/ionstack-part-2/)
- [使用者提供的 HackMD 漏洞索引](https://hackmd.io/@lokey0905/rk-hQSzibl)
