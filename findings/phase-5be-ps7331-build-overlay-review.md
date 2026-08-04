# Phase 5BE：PS7331 build patch／overlay 邊界檢查

日期：2026-08-04
裝置：Amazon Fire HD 10 2021，`KFTRWI`／`trona`／MT8183
目前安裝版本：Fire OS 7.3.3.0，`PS7330.4104N`

## 目的與範圍

本階段只回答一個升級前的主機端問題：7.3.3.1 官方 source bundle 中，是否
存在尚未被前一輪抽取的 kernel patch、patch series、build overlay 或 build
script 步驟，足以解釋為何 source 的 `remove_waiter()` 看起來是舊語意、但
PS7331 signed Image 可能不同。

檢查使用官方 7.3.3.1 source URL，串流列出 outer archive 的 nested
`platform.tar` 路徑；不保存完整 source、不抽取新 source member、不執行 source、
不編譯 kernel，也沒有任何 ADB、bootloader 或分割區操作。

## 結論先行

### 已證實

1. Nested inventory 的四段 pipeline 全部成功：`curl=0`、`bzip2=0`、
   `outer_tar=0`、`nested_tar=0`、`filter=0`。這是完整串流 path listing 的
   成功證據，而非抽取或編譯證據。

2. 對 inventory 結果再以 `.patch`、`.diff`、`patch/`、`patches/`、`series`
   與 `quilt` 做精確子集篩選，只得到同一個 Mali hrtimer patch 的四個
   variant path：

   - `kernel/mediatek/4.4/.../mali-r7p0/Patch/hrtimer_639418_r7p0_ipbase.diff`
   - `kernel/mediatek/4.4/.../mali-r7p0_v2/Patch/hrtimer_639418_r7p0_ipbase.diff`
   - `kernel/mediatek/mt8183/4.4_emc/.../mali-r7p0/Patch/hrtimer_639418_r7p0_ipbase.diff`
   - `kernel/mediatek/mt8183/4.4_emc/.../mali-r7p0_v2/Patch/hrtimer_639418_r7p0_ipbase.diff`

   沒有出現 `rtmutex`、`futex`、`remove_waiter`、`proxy_owner` 或
   `GhostLock` 命名的 patch／diff／series path。此結論的範圍是 path name，
   不是未命名 generated transformation 的絕對不存在。

3. 官方 build script 的可見流程是：下載 toolchain、extract platform tar、
   執行 `trona_defconfig`、執行 full `make`、複製 ARM64 boot output、驗證
   image。可見 script 沒有 `git apply`、`patch`、`quilt`、`series` 或額外
   rtmutex overlay 步驟。build config 明確指定：

   ```text
   KERNEL_SUBPATH=kernel/mediatek/mt8183/4.4
   DEFCONFIG_NAME=trona_defconfig
   TARGET_ARCH=arm64
   ```

4. build-selected `mt8183/4.4/kernel/locking/rtmutex.c` 的 source hash 是
   `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`；既有
   semantics checker 仍觀察到 `current->pi_blocked_on` cleanup、沒有
   `waiter->task` reference，且 proxy error path 仍呼叫 `remove_waiter()`。

5. PS7331 reconstructed signed Image 的既有 binary review 也在
   `remove_waiter` 觀察到由 `SP_EL0` 取得 current-task source 並經由該指標
   清除欄位，與 source-level pre-fix pattern 一致。這是 PS7331 binary 的
   inspected-function 證據，不是 exploit 或 root 結果。

### 高可信推論

- 在目前可取得的官方 source package、可見 build script、build-selected
  source 與 PS7331 signed Image 證據中，沒有支持「未保存的 rtmutex build patch
  修掉 GhostLock」的線索。
- 因 GhostLock 而升級到 PS7331，目前沒有充分證據支持其能修補
  CVE-2026-43499 的核心 `remove_waiter()` 語意。這個判定不延伸成「PS7331
  沒有其他安全修補」。
- 7.3.3.1 若要作一般安全更新 A/B，應使用官方完整 OTA 流程；它不是可由
  `boot.img` 單獨替代的可逆 mutation。

### 待驗證

- source package 外部 CI／release environment 是否曾在 archive 外套用未命名
  generated patch；本檢查沒有執行 Amazon build environment，因此不能排除
  所有 archive 外的 build infrastructure。
- PS7330 installed signed Image 的 exact `remove_waiter()` binary semantics；
  shell 仍無法讀取已安裝 boot block。
- PS7331 其他 kernel／Android／vendor security change；本階段只針對
  GhostLock rtmutex boundary 與 build packaging。

### 已排除／不採用

- 把 Android boot header 的 `kernel_offset=0x800` 當成 runtime kernel offset
  或 exploit offset。
- 把 4 個 Mali hrtimer patch path 解讀為 rtmutex／GhostLock 修補。
- 把 source path inventory 或 source-level PI path 存在解讀成可取得 root。
- 把 PS7331 `boot.img` 單獨寫入 PS7330 當作升級方案。

### 因風險拒絕測試

- 完整 OTA sideload、fastboot／BROM／DA、preloader／LK 操作。
- boot、system、vendor、TEE、userdata 或其他分割區寫入。
- futex race、GhostLock reproducer、kernel memory access、未知 ioctl、root
  payload 或 SELinux／kernel 修改。

## 證據與可重現性

| Evidence | Observation | Classification |
|---|---|---|
| `P5BE-INV-001` | Nested source path listing 全部 pipeline exit 0 | 已證實，path-inventory scope |
| `P5BE-INV-002` | 精確 patch/diff/series 子集只有 4 個 Mali hrtimer paths | 已證實，path-name scope |
| `P5BE-BUILD-001` | build script 只顯示 extract、defconfig、make、copy、validate，沒有可見 patch apply | 已證實，script scope |
| `P5BE-SOURCE-001` | build-selected rtmutex source retains pre-fix pattern | 已證實，source scope |
| `P5BE-BINARY-001` | PS7331 Image inspected `remove_waiter` retains current-task pattern | 已證實，binary inspected-function scope |
| `P5BE-OTA-001` | PS7331 is a full block OTA writing multiple partitions | 已證實，OTA metadata scope |
| `P5BE-DEVICE-001` | Current device remains PS7330/ADB device/HOME Fire Launcher | 已證實，device snapshot scope |

## 升級決策

### GhostLock 研究目的：暫不升級

目前最小、可重現的證據鏈是：

```text
PS7331 build-selected source: old current-task cleanup
        +
PS7331 reconstructed signed Image: same inspected pattern
        +
PS7331 focus config: no relevant FUTEX/RT_MUTEX change
        ↓
PS7331 is not a demonstrated GhostLock remediation
```

所以 7.3.3.1 不應僅因為「有 boot.img／source」就被當成 GhostLock 修補版。

### 一般安全更新：可列入候選，但不是本輪執行項目

若研究目標改為比較 Amazon 一般安全更新，PS7331 可以列為後續 A/B 候選；
但現有 OTA metadata 顯示它是 `trona` 的 full block OTA，除 system/vendor/boot
外還涉及 preloader、LK、TEE、SPMFW、SSPM 與 camera VPU 分割區。這不符合
「只換 boot.img、可隨時還原」的條件，也沒有在本輪執行升級。

## 可重產命令

先只看計畫：

```sh
tools/scripts/index_phase5_ps7331_nested_build_patches.sh --dry-run \\
  --url https://fireos-tablet-src.s3.amazonaws.com/k2k5jkgocvaww3SgOjJMkJrykI/Fire_HD10-7.3.3.1-20250617.tar.bz2 \\
  --output artifacts/phase5/reproduction-ps7331-nested-build-patch-index
```

實際執行會串流列出 nested `platform.tar` 路徑，只建立新的 output directory；
不會保存完整 archive、執行 source 或連接裝置。既有結果與 SHA-256 位於：

`artifacts/phase5/ps7331-nested-build-patch-index-20260804-01/`

## 最終狀態

本報告完成時未執行升級。裝置仍為 PS7330.4104N、ADB state=`device`，HOME
仍為 `com.amazon.firelauncher/.Launcher`。PS7331 保留為經 hash 驗證的主機端
相鄰版本 reference，不把它標成已安裝版本。
