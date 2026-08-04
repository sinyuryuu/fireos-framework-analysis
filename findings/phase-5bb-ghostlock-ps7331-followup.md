# Phase 5BB：PS7331 source／boot follow-up 與 GhostLock 升級決策

日期：2026-08-04  
裝置：Amazon Fire HD 10 2021，`KFTRWI`／`trona`／MT8183  
目前安裝版本：Fire OS 7.3.3.0，`PS7330.4104N`

## 結論先行

### 已證實

1. 本輪沒有修改裝置。最後唯讀檢查仍為：

   ```text
   Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys
   priority=50 ... com.amazon.firelauncher/.Launcher
   ```

2. 7.3.3.1 的官方相鄰 OTA／boot artifact 已在主機端保存並核對：

   ```text
   post-build=Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys
   post-security-patch-level=2024-08-01
   boot.img SHA-256=cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b
   ```

3. PS7331 signed kernel Image 的離線分析在 `remove_waiter` 中找到
   `SP_EL0` current-task 來源及透過該 current task 清理欄位的 pattern；
   `rt_mutex_start_proxy_lock` 的 proxy error path 仍呼叫 `remove_waiter`。
   這與 CVE-2026-43499 修補前的語意一致。分析只使用主機端 Image，不執行
   kernel code，也沒有產生 runtime address 或 exploit payload。

4. PS7330 與 PS7331 的 3,705 個 kernel config key 只有三項差異，GhostLock
   關聯的 `CONFIG_FUTEX`、`CONFIG_RT_MUTEXES`、`CONFIG_PREEMPT`、
   `CONFIG_RANDOMIZE_BASE`、ARM64 4K／VA39 等 focus key 沒有差異。

5. 7.3.3.1 source bundle 的 build scripts 將 kernel source 指向
   `kernel/mediatek/mt8183/4.4`、`trona_defconfig`、`arm64`；外層 archive
   是包含 nested platform source input 的 packaging。

6. 已從 nested `platform.tar` 抽出 build-script 指向的
   `kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`。它的
   `remove_waiter()` 仍使用 `current->pi_lock`、`rt_mutex_dequeue()` 後清除
   `current->pi_blocked_on`；`rt_mutex_start_proxy_lock()` 的 error path 仍
   呼叫 `remove_waiter()`。相對於 pinned v4.4.146 old reference，該檔案的
   source diff 僅是 `rt_mutex_proxy_unlock()` 介面變更，沒有 `waiter->task`
   修補。

7. 同一 nested archive 另有 `kernel/mediatek/4.4` legacy tree；該 tree 的
   `rtmutex.c` normalized SHA 與 PS7330 source／v4.4.146 reference 都是
   `c4ddac5fe820c7f07670bc332425be05b0df0400ae334a147b483f0ee9b07345`。
   但它不是 build script 指定的 `mt8183/4.4` tree，不能取代 build-selected
   tree 的證據。

### 高可信推論

- **不建議為了 GhostLock 單獨升級到 PS7331。** 目前最直接的 PS7331
  compiled evidence 顯示 inspected `remove_waiter` 仍是舊的 current-task
  cleanup pattern；config comparison 也沒有提供修補線索。
- PS7331 可能包含其他 Android／Amazon 安全修補，不能把「GhostLock 未見修補」
  推廣成「整個 7.3.3.1 不值得升級」。若研究目標改為一般安全更新 A/B，升級可
  另立版本實驗；那不是可逆的普通 mutation。
- 目前仍不能從 PS7331 boot.img 推導出 PS7330 的可用 kernel runtime offset，
  也不能由 public source 單獨證明 privilege transition 或 root exploit 可達。
- 7.3.3.1 build-selected source 與 signed Image 都指向同一個 pre-fix
  `remove_waiter()` 語意；因此「PS7331 已修補 GhostLock」現在缺乏支持，
  而「PS7331 不是已證明的 GhostLock remediation」具備 source／binary 雙重
  證據。

### 待驗證

- 7.3.3.1 source 中尚未抽出的 `trona_defconfig` 與完整 build-input 選擇；
  已抽出的 `mt8183/4.4` kernel source 已足以判斷關鍵
  `remove_waiter()` 語意，但不能代表 source package 所有 patch。
- PS7330 installed signed Image 是否與公開 7.3.3.0 source 完全一致；目前
  shell 無法讀取 exact boot block，因此只有 source/config candidate，不是
  signed-binary confirmation。
- PS7331 的其他 kernel path 或 Android policy 是否改變 GhostLock reachability。

### 已排除

- 「CVE 在 2026 公開，所以 PS7331 必然未修補」不是證據。現在有 compiled
  old-pattern evidence，但仍需把結論限於 inspected function。
- 「拿 PS7331 `boot.img` 單獨寫入 PS7330 即可安全升級」沒有成立。boot、system、
  vendor、LK、preloader、AVB／rollback 與 OTA transaction 的配套尚未被證明。
- 已執行過的 `mtk-su64`／MTK-SU payload 不是新候選；其 exact test 已在
  `MTK-SU-CMDQ-T03` 的 critical init step 3 失敗，本輪不重跑。

### 因風險拒絕測試

- 沒有執行 futex race、GhostLock reproducer、kernel memory read/write、
  ION／CMDQ ioctl、root payload、BROM／DA、LK／preloader、fastboot flash／
  unlock、OTA sideload 或任何 partition write。
- 沒有安裝、啟動或執行來源不明的 root／exploit APK 或 binary。
- 沒有把 7.3.3.1 boot.img 寫入裝置，也沒有重開機升級。即使研究者接受變磚，
  這些操作仍無法在目前 artifact 不完整時產生可歸因的科學證據。

## 證據鏈

```text
PS7330 exact public source + live config
        └─ old rtmutex/futex source family

PS7331 official adjacent boot Image
        └─ compiled remove_waiter still reads current from SP_EL0
           and proxy rollback still calls remove_waiter

PS7330 / PS7331 focus config comparison
        └─ no GhostLock-related config change

        ↓

PS7331 is not a demonstrated GhostLock remediation.
```

這個結論是 patch-status／升級決策，不是漏洞可利用性或 root 結果。

## PS7331 artifact 對照

| 項目 | 值 | 證據 |
|---|---|---|
| Product | `trona` | PS7331 OTA metadata |
| Build | `PS7331.4463N/0031575863040` | `ota.prop`／OTA metadata |
| Security patch | `2024-08-01` | OTA metadata |
| Boot image SHA | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` | boot inspection |
| Kernel format | gzip-compressed ARM64 Image | boot inspection |
| Kernel address in Android header | `0x40080000` | boot inspection |
| Kernel offset in Android header | `0x800` | boot inspection |
| Kernel banner | `Linux 4.4.146+`／`PREEMPT` | decompressed Image |
| Source build path | `kernel/mediatek/mt8183/4.4` | `build_kernel.sh` |
| Defconfig | `trona_defconfig` | `build_kernel_config.sh` |

Android boot header offset/address are image-layout metadata. They are not a
runtime KASLR slide, symbol address, `task_struct` offset, or exploit offset.

## GhostLock patch boundary

NVD describes CVE-2026-43499 as the `remove_waiter()` proxy-lock rollback bug in
which the old code uses `current` instead of `waiter->task`; the upstream fix is
listed as commit `3bfdc63936dd4773109b7b8c280c0f3b5ae7d349`. The observed PS7331
compiled pattern maps to the pre-fix semantic shape. See [NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499).

The exact PS7330 public source has the same old source-level pattern and is
normalized byte-identical to the pinned v4.4.146 old reference. That is strong
source/config evidence for PS7330, but the installed signed binary remains a
separate evidence boundary.

The build-selected PS7331 source tree also contains a separate vendor API delta:
`rt_mutex_proxy_unlock()` loses its `proxy_owner` parameter, while the preserved
function body still references `proxy_owner`. This is recorded as a source-tree
consistency caveat, not as a compiler result; the source was not built. It does
not change the direct observation that `remove_waiter()` still clears
`current->pi_blocked_on`.

## Upgrade decision

### Current decision: do not upgrade yet for this research question

The upgrade is not being rejected as a general Fire OS security update. It is
deferred because the available evidence does not show that PS7331 fixes the
specific GhostLock root cause, while changing the installed build would remove
the clean PS7330 baseline and may not be reversible.

Before considering a normal official update, complete these host-only steps:

1. The nested platform member has now been located and the relevant
   `rtmutex.c`, `futex.c`, `rtmutex_common.h`, and `sched.h` members have been
   extracted. Preserve their hashes and source diffs in the artifact directory.
2. Treat the build-selected `mt8183/4.4` source as the authoritative source
   candidate; keep the legacy `kernel/mediatek/4.4` tree separate.
3. Record the full official OTA metadata, hashes, device/product match, and the
   recovery/update path offered by the device. Do not substitute a standalone
   boot image for the complete update transaction.
4. If upgrading for general security research, freeze the PS7330 baseline and
   define the post-update collection before changing the device. Treat the
   update as a potentially non-reversible system mutation, not as a routine
   reversible test.

## Reproduction

All commands below are host-only or read-only against preserved artifacts:

```sh
python3 tools/scripts/compare_phase5_ps7330_ps7331_kernel.py --dry-run \
  --ps7330-config adb/phase5/PHASE5AQ-DEVICE-CONFIG-20260804-02/kernel.config \
  --ps7331-config artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config \
  --ps7331-boot firmware/extracted/PS7331/boot.img \
  --output artifacts/phase5/phase5ba-ps7331-upgrade-comparison-20260804-01
```

The PS7331 static review is reproducible with the existing
`analyze_phase5ar_ps7331_rtmutex_binary.py` workflow. The device post-check is
stored in `adb/phase5/PHASE5BA-DEVICE-POSTCHECK-20260804-01/` and reports the
PS7330 fingerprint, HOME resolver, Fire Launcher path, and ADB state.

The nested source index is in
`artifacts/phase5/exact-kernel-source-review-7331-nested-platform-index-20260804-01/`.
The selected source members and source-only comparisons are in
`artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/`
and
`artifacts/phase5/exact-kernel-source-review-7331-source-comparison-20260804-01/`.
The selected extraction returned an expected nonzero status only because the
requested `mt8183_defconfig` path was absent; the build-selected kernel source
members were extracted successfully. The missing defconfig is not silently
treated as a successful extraction.

To reproduce the selected-member extraction on a fresh output directory:

```sh
bash tools/scripts/extract_phase5_nested_kernel_members.sh \
  'https://fireos-tablet-src.s3.amazonaws.com/k2k5jkgocvaww3SgOjJMkJrykI/Fire_HD10-7.3.3.1-20250617.tar.bz2' \
  artifacts/phase5/reproduction-ps7331-nested-kernel-members
```

## Scope note

This report intentionally does not provide exploit offsets, payload construction,
futex race instructions, or privilege-escalation steps. The project remains a
static／controlled Fire OS analysis and does not claim root access.
