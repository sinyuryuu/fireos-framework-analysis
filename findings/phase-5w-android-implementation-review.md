# Phase 5W：Android 實作、MediaTek boot-chain 與 exact PS7330 適用性審查

## 目的與範圍

本輪回答「這些 CVE 在 Android 中實際落在哪一層，以及公開 Android
implementation 能否對應到 KFTRWI/trona/MT8183/PS7330」；不把公開 PoC、Android
API 或相鄰版本 image 直接當成本機 root 方法。

本輪是主機端與既有證據的離線分析，沒有重新執行已完成的 CMDQ、IMS/ATCI、
Bluetooth、futex 或 bootloader 測試。沒有啟用 Bluetooth，沒有寫入 ATCI property，
沒有啟動 vendor daemon、開啟 ATCI socket、發送 HCI/AT 資料、開啟新的 device-node，
沒有執行 native binary／exploit，沒有進入 BROM/DA、fastboot 或 recovery，也沒有
讀寫任何分割區。

可重現分析器：

`tools/scripts/analyze_phase5w_android_implementations.py`

衍生 artifact：

`artifacts/phase5/android-implementation-preloader-review-20260804-02/`

該 artifact 只保存報告與相鄰 PS7331 image 的 hash、篩選後 printable strings 和
implementation map；未把大型 image 或任何 exploit binary 推入公開輸出。

## exact target baseline

| 欄位 | 觀察值 | 證據 |
|---|---|---|
| Model / product | KFTRWI / trona | `findings/phase-5t-ota-metadata-review.md` |
| SoC | MT8183 | `findings/phase-5t-ota-metadata-review.md` |
| Android | 9 / API 28 | same |
| Build fingerprint | `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys` | same |
| Fire OS | 7.3.3.0 / PS7330 / 4104 | same |
| Security patch | 2024-02-01 | same |
| Verified Boot | green; `ro.boot.flash.locked=1` | prior read-only baseline |
| Kernel source family | Amazon/MediaTek 4.4; exact signed binary unavailable | `findings/phase-5o-exact-futex-sched-review.md` |
| Android HOME | `com.amazon.firelauncher/.Launcher` | existing Phase 3 evidence |
| boot descriptors | PL `d1a4a4b-20231011_072631`, LK `79172a1-20231008_072039` | Phase 5T raw capture |

本輪使用的 boot-chain image 不是設備上安裝的 image：

| local input | SHA-256 | status |
|---|---|---|
| `firmware/extracted/PS7331/images/preloader.img` | `25d8d377d059ec3d5117aa4e749f4f54ef1bfbe8153ae51b309bf20d30eed904` | `VERSION_MISMATCH` |
| `firmware/extracted/PS7331/images/lk.img` | `1f52e5700058df32ffceeed3fb46d7867f8cc3463286f8177cf17dfcf80de495` | `VERSION_MISMATCH` |

因此下面所有 PS7331 string 結論都只代表「相鄰版本 image 內存在這些字串」，
不代表本機 PS7330 binary 的控制流、offset、patch status 或可達性。

## Android 實作分層

```text
Android app / native test / Bionic syscall
        |
        +-- framework service boundary (IMS, Bluetooth, Settings, CTS)
        |
        +-- vendor Android implementation (MediaTek IMS/ATCI, ION, CMDQ, BT)
        |
        +-- kernel driver / futex-rtmutex / vendor HAL
        |
        +-- preloader / LK / BROM (Android userspace 尚未啟動)
```

關鍵判斷是：Android 公開 source 能說明「進入哪個介面」，但漏洞是否存在於
Amazon exact binary、是否有 shell 可達路徑、以及是否需要更高權限，必須分開驗證。

## CVE 與 Android implementation 對照

### CVE-2026-43499（GhostLock）

**Android 實作位置：Linux kernel，不是 APK。** Android native code 可以經由
Bionic／`syscall` 進入 futex PI；核心路徑再進入 futex／rtmutex。官方修補的
source-level 語意是 `remove_waiter()` 使用 `waiter->task`，並同步修正該 task 的
priority-chain rollback，而非使用不正確的 `current`。

本機 exact Amazon source/config 證據：

- `CONFIG_FUTEX=y`、`CONFIG_RT_MUTEXES=y`、`CONFIG_PREEMPT=y`，且
  `CONFIG_PANIC_ON_OOPS=y`：`artifacts/phase5/exact-kernel-source-review-20260804-01/members/mt8183_defconfig.e1495a4e51db.txt`；
- Amazon `rtmutex.c` 與 pinned stable v4.4.146 的 normalized comparison 保留
  舊 proxy rollback pattern：`artifacts/phase5/exact-kernel-source-review-20260804-02/rtmutex-comparison.json`；
- vendor `sched.h` 有 MTK/WALT/config-dependent `task_struct`，所以 upstream
  source 不能直接推出 compiled `pi_blocked_on` offset：
  `findings/phase-5o-exact-futex-sched-review.md`。

**結論：**

- **已證實：** Android/kernel source family 存在 GhostLock 相關 futex/rtmutex
  路徑。
- **高可信推論：** 這是 source/config applicability，不是本機 root exploit 證明。
- **待驗證：** signed PS7330 kernel 是否有 backport、compiled layout、KASLR 和
  shell domain 的完整觸發條件。
- **因風險拒絕測試：** futex PI race、kernel write、panic/reboot、SELinux/root
  stage，以及其他裝置的 target header／offset 移植。

### CVE-2022-20053（IMS missing authorization）

**Android 公開實作位置：AOSP telephony IMS service binding。** Android 9 的
`android.telephony.ims.ImsService` 是一個由 framework 綁定的 `Service`；manifest
要宣告 `android.permission.BIND_IMS_SERVICE` 和
`android.telephony.ims.ImsService` intent。framework 會依 device overlay 的
`config_ims_package` 或 carrier override 選擇要 bind 的 IMS service。這是 Android
層的正常服務契約，不是 MediaTek 漏洞實作本身。

本機 runtime 已有更直接的限制證據：

- package/service/process filter 沒有 active IMS package、`ims` 或 `atcid` service；
- `/vendor/etc/init/atcid.rc` 內的 `atcid-daemon-u` 是 `disabled`、`oneshot`，需
  明確 property 條件才會 start；
- shell 無法 pull/hash `/vendor/bin/atcid`。

**結論：**

- **已證實：** AOSP Android 9 有 IMS framework implementation boundary；本機
  正常 runtime snapshot 沒有 active IMS/ATCI endpoint。
- **待驗證：** Amazon/MediaTek vendor binary 是否已修補 CVE-2022-20053。
- **已排除：** 目前正常 ADB shell 可直接抵達 active IMS service 的說法。

### CVE-2022-20054（IMS／AT command injection）

**Android 實作位置：MediaTek vendor IMS/ATCI，不是 AOSP generic ImsService。**
AOSP 只提供 service binding、permission 和 feature lifecycle；ATCI HIDL、
`atcid-daemon-u`、`adb_atci_socket`、modem command routing 屬於 vendor layer。

保存的 exact init 片段顯示：

```text
service atcid-daemon-u /vendor/bin/atcid
    interface vendor.mediatek.hardware.atci@1.0::IAtcid default
    socket adb_atci_socket stream 660 radio system
    disabled
    oneshot

on property:persist.vendor.service.atci.autostart=1
    start atcid-daemon-u
```

這段是「存在一個受條件控制的 vendor implementation」的證據，不是可用的
shell exploit 入口。任何設定 property、start service、開 socket、送 AT command
或呼叫未知 Binder 都會跨越本輪安全界線。

**結論：**

- **已證實：** 官方 MediaTek bulletin 將 CVE-2022-20054 描述為 IMS 中缺少
  permission check 導致 AT command injection，並列 MT8183／Android 9–12。
- **已證實，snapshot-scoped：** 本機正常 runtime 沒有 active ATCI service，且
  vendor executable 對 shell 不可讀。
- **未知：** exact PS7330 vendor binary 的 patch status。
- **因風險拒絕測試：** property/service/socket/AT/Binder 觸發與漏洞輸入。

### CVE-2022-20055／20056（preloader USB OOB）

**Android 實作位置：不在 Android userspace。** 這類問題發生在 preloader 的
USB download/parser path，在 kernel、system_server、APK 和 AOSP telephony 之前。
因此不存在可由一般 Android app 或 AOSP API 代表的「Android implementation」。
公開 Android 內容只能幫助辨認裝置版本和 boot-chain 邊界，不能取代 exact
preloader binary。

MediaTek 2022-03 公告把 20055、20056 描述為 preloader USB OOB write，列出
MT8183，但 affected software versions 是 Android 10/11/12；這與本機 Android 9
Fire OS 不完全匹配。NVD 的 20056 也將受影響 Android CPE 列在 10/11/12。

相鄰 PS7331 preloader 的 host-only strings 顯示：

- anti-rollback／RPMB image-version checks；
- DA length overflow／DA RAM bounds diagnostics；
- LK DA authentication、signature／public-key diagnostics；
- USB enumerate/listen/timeout 與 download path；
- MT8183、`MTK_BLOADER_INFO_v36`、`preloader_trona.bin`。

相鄰 PS7331 LK 則含有：

- production／engineering image authentication strings；
- `amzn_verify_unlock`、temporary-unlock API names；
- fastboot／unlock status strings；
- MT8183 platform references。

這些字串只證明 image 內含安全啟動與 Amazon unlock 相關程式碼的名稱；不證明
存在 bypass，也不證明 PS7330 有相同版本或相同 offset。

**結論：**

- **已證實：** 相鄰 PS7331 image 有 USB download、DA authentication、anti-rollback
  和 Amazon LK unlock-related string evidence。
- **高可信推論：** 盲目把 PS7331 或 generic MTK preloader/DA 套用到 PS7330 可能
  失敗、進入死循環或造成不可恢復狀態。
- **已排除：** 把這些 preloader strings 稱為 Android 9 shell 可用的 root 方法。
- **因風險拒絕測試：** preloader handshake、BROM/DA、USB malformed input、
  preloader/LK/seccfg/partition write。

### CVE-2020-0069（CMDQ）

**Android 公開實作位置：AOSP CTS native test，而非一般 APK。** AOSP CTS 的
公開測試以 native `cc_test`／`poc.c` 形式存在，依賴歷史 MediaTek CMDQ v2
request contract。這個 implementation 只能作 ABI／版本對照，不能視為安全的
安裝包。

Fire exact source 對照與已封存的一次 read-only request 顯示：

- MT8183 build selects CMDQ v3；
- v3 dispatcher 沒有被測 v2 request #7 的 case；
- 已保存 request #7 result 是 `-ENOTTY`；
- 沒有重試、非零參數、DMA/physical-address path 或其他 ioctl。

**結論：** 已排除的是「已測的 v2 CMDQ route」，不是所有 CMDQ code 都被 binary-level
證明安全。這條 route 不應再重複。

### CVE-2023-20616（ION）

**Android 公開實作位置：ION userspace ABI + vendor driver。** Android ION header
提供 `ION_IOC_CUSTOM` request shape；MediaTek 的 custom subcommand dispatch
位於 vendor driver，不是 AOSP framework 本身。Phase 5M 的 host-only disassembly
已從 `libion_mtk.so` 恢復 custom ioctl constant 和 helper call sites，但沒有
開啟 `/dev/ion` 或發送 request。

MediaTek 2023-02 公告所列 MT8183 row 是 Android 11/12 software family，不能直接
套用到本機 Android 9。這裡沒有 exact PS7330 patched/unpatched binary 對照。

**結論：** **待驗證／不值得 live trigger**；目前只保留 ABI 和版本 mismatch
證據，不新增 ioctl 實驗。

## 公開 GitHub Android implementation 參考

這一節沿用 Phase 5O 的 pinned public-source review，不下載、編譯、安裝或執行
第三方 APK/native binary：

| 專案 | 實際定位 | 與本機差異 | 可借鑑內容 |
|---|---|---|---|
| [`CakesTwix/Android-CVE-2026-43499`](https://github.com/CakesTwix/Android-CVE-2026-43499) | Android detector／結果判定 app | 不是通用 root implementation，也沒有 `trona` target | Android packaging、ABI detector 與「不要把 detector 當 exploit」的區分 |
| [`xianwan1314/CVE-2026-43499-Poc-Analysis`](https://github.com/xianwan1314/CVE-2026-43499-Poc-Analysis) | 依 boot image／profile 產生 target header 的移植框架 | 需要 exact boot/vmlinux；沒有 KFTRWI/PS7330 profile | 每個 build 重新建立 layout/profile 的方法 |
| [`NothingFumo/ghostlock-aresin`](https://github.com/NothingFumo/ghostlock-aresin/commit/1895a89c52dc7d7355f14babe5009c2932dcdb6a) | POCO F3 GT／MT6893／Android 13／Linux 4.14.186 target | 不同 SoC、Android、kernel line；不是 Fire target | target-specific source/layout 驗證流程 |
| [`soralis0912/CVE-2026-43499-aristotle`](https://github.com/soralis0912/CVE-2026-43499-aristotle) | MediaTek Android 12／5.10.136 研究 target | 不同 kernel/裝置，README 也沒有本機 profile | static-analysis 到 target profile 的研究方法 |

先前保留的 bounded repository search 沒有找到可驗證的
`KFTRWI/trona/MT8183/PS7330` exact Android implementation。這個結果只代表已
記錄的搜尋範圍，不能宣稱全網不存在其他研究。對本專案而言，最重要的差異不是
「同樣是 Android」，而是 kernel line、vendor patch、compiled layout、boot
descriptor、SELinux/permission context 和 exact signed artifact。

**判定：**

- **已證實：** 公開 Android projects 可提供 detector、target-generation 或
  device-specific port 的方法參考。
- **高可信推論：** 沒有 exact PS7330 profile 時，複製其他裝置的 offset／target
  header 不能形成可驗證本機 implementation。
- **因風險拒絕測試：** 安裝 detector、執行 native payload、futex trigger 或
  以錯配 profile 進行 root stage。

## 官方 scope 與版本適用性矩陣

| CVE / family | Android implementation | MT8183 | Android 9 scope | 本機可達性 | 判定 |
|---|---|---:|---:|---|---|
| 2026-43499 | kernel futex/rtmutex | source family | kernel 4.4 source overlap | 未建立安全 trigger | source-only |
| 2022-20053 | AOSP IMS + vendor IMS | 是 | 是 | normal snapshot 無 active endpoint | 不可由目前 shell 路徑驗證 |
| 2022-20054 | vendor IMS/ATCI | 是 | 是 | service disabled、binary unreadable | route rejected |
| 2022-20055/56 | preloader USB | 是 | 公告列 10–12 | 需物理 boot-chain path | version mismatch |
| 2020-0069 | CTS native -> CMDQ | historical MTK | historical route | tested v2 request `-ENOTTY` | tested route disproved |
| 2023-20616 | ION ABI -> vendor driver | 是 | 公告列 11/12 | 未開 device node | version mismatch / unknown |

## 公開 Android implementation 的可移植性結論

### 可以移植的部分

1. **分層與介面辨識：** 可以用 AOSP `ImsService`、CTS CMDQ test、ION header、
   Linux `rtmutex.c` 分辨 framework、native driver、kernel 和 preloader 邊界。
2. **source-level comparison：** 可以比對 Fire source 與 upstream 的控制流、
   Kconfig、ioctl request shape 和 Android service manifest contract。
3. **compatibility gating：** 可以先用 SoC、Android API、kernel line、build
   descriptor、patch level 和 binary hash 排除明顯錯配。

### 不能直接移植的部分

1. 其他手機的 `target.h`、KASLR/physmap、`task_struct` offset、stack profile；
2. generic MTK preloader/DA、payload 或 bootloader unlock flow；
3. 其他 Android 版本的 vendor IMS/ATCI、ION、Bluetooth 或 preloader binary；
4. AOSP CTS PoC 作為普通 APK 或 shell-safe probe；
5. 由「官方 affected scope」推導 exact Amazon binary 未修補。

## Evidence-indexed verdict

| Evidence ID | 結論 | 來源 | 狀態 |
|---|---|---|---|
| `P5W-ANDROID-001` | GhostLock 的 Android 入口是 native futex syscall，核心修補在 rtmutex，不是 APK | Linux patch；`findings/phase-5o-exact-futex-sched-review.md` | 已證實，implementation scope |
| `P5W-FIRE-001` | Fire source/config 有 futex/rtmutex 家族，但 signed binary/layout 未取得 | exact defconfig、rtmutex comparison artifacts | 已證實，source/config scope |
| `P5W-ANDROID-002` | AOSP Android 9 `ImsService` 以 framework binding/permission/overlay contract 實作 | AOSP `ImsService.java` | 已證實，AOSP scope |
| `P5W-ANDROID-003` | CVE-2022-20054 的 ATCI 是 MediaTek vendor layer；本機 normal snapshot 無 active service | `findings/phase-5i-ims-atci-triage.md` | 已證實，snapshot scope |
| `P5W-WEB-001` | MediaTek bulletin 列 20054 為 IMS AT command injection、MT8183、Android 9–12；20055/56 為 preloader USB、MT8183、Android 10–12 | [MediaTek March 2022 bulletin](https://corp.mediatek.com/product-security-bulletin/March-2022) | 已證實，external-scope |
| `P5W-PL-001` | PS7331 preloader strings 顯示 anti-rollback、DA auth、USB download path | `artifacts/phase5/android-implementation-preloader-review-20260804-02/preloader-selected-strings.tsv` | 已證實，adjacent-image scope |
| `P5W-LK-001` | PS7331 LK strings 顯示 production auth、Amazon temporary-unlock names、MT8183 | `.../lk-selected-strings.tsv` | 已證實，adjacent-image scope |
| `P5W-ANDROID-004` | CVE-2020-0069 public Android implementation 是 CTS native CMDQ v2 test；Fire tested v2 request route 不匹配 v3 | `findings/phase-5q-android-cmdq-implementation-review.md` | 已證實，tested-route scope |
| `P5W-ANDROID-005` | ION public Android side is ABI/helper mapping only; no exact Android 9 live applicability | `findings/phase-5m-evidence-index.md`; `findings/phase-5u-android-cve-applicability.md` | 高可信推論／未驗證 binary |
| `P5W-GH-001` | Detector、target-generator、MT6893/Android 13 port 和 MTK Android 12 port 都沒有 exact `trona/PS7330` profile | `findings/phase-5o-android-public-poc-review.md`; `findings/phase-5p-android-nearby-port-review.md` | 已證實，bounded public-source scope |
| `P5W-SAFE-001` | 本輪沒有裝置狀態變更或 exploit/boot-chain action | artifact `result.md`、commands、hash manifest | 已證實 |

## 最終判定

- **已證實：** 「Android 的實作」不是單一 APK。GhostLock 在 kernel；IMS/ATCI
  分成 AOSP binding 與 MediaTek vendor service；CMDQ/ION 是 Android native ABI
  進入 vendor driver；preloader USB 則在 Android userspace 之前。
- **高可信推論：** 對這台 PS7330，公開 Android implementation 最有價值的是
  版本／ABI／權限邊界分析，不能直接生成可安全執行的 root payload。
- **已排除：** 用 generic Android PoC、其他 MTK 機型的 offset、PS7331 image 或
  AOSP CTS binary 直接測本機的做法。
- **待驗證：** exact PS7330 preloader/LK/vendor IMS/ION/Bluetooth binary 的
  patch state；目前 shell 沒有合法可讀取的完整 matching artifact。
- **因風險拒絕測試：** 所有需要 boot image/block read、BROM/DA、preloader
  handshake、vendor modem command、Bluetooth/HCI、futex PI 或 malformed ioctl
  的 live action。

## 可重現指令

先做不寫入的驗證：

```sh
python3 tools/scripts/analyze_phase5w_android_implementations.py --dry-run \
  --device-report findings/phase-5t-ota-metadata-review.md \
  --ims-report findings/phase-5i-ims-atci-triage.md \
  --preloader-report findings/phase-5-mtk-compatibility-review.md \
  --preloader firmware/extracted/PS7331/images/preloader.img \
  --lk firmware/extracted/PS7331/images/lk.img \
  --output artifacts/phase5/android-implementation-preloader-review-20260804-02
```

原始輸入 hash、命令、選取字串和 derived manifest 位於：

`artifacts/phase5/android-implementation-preloader-review-20260804-02/`

該目錄中的 `sha256sums.txt` 應在目錄內執行 `shasum -a 256 -c sha256sums.txt`。
