# Phase 5BC：GhostLock source semantics 與 exact-target route boundary

日期：2026-08-04
目標：在不觸發 kernel、root 或 boot-chain 操作的前提下，將 PS7331
build-selected source 的 GhostLock 判定機械化，並重新審核公開 Android route。

## 結論

### 已證實

1. 對 PS7331 build script 指定的
   `kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` 執行 host-only
   semantics checker，結果是：

   ```text
   PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN
   current->pi_blocked_on cleanup: true
   waiter->task reference in remove_waiter: false
   proxy error remove_waiter call: true
   ```

2. PS7331 legacy `kernel/mediatek/4.4/rtmutex.c` 也得到相同分類；其 hash
   與 pinned v4.4.146 old reference 相同。build-selected tree 雖有
   `rt_mutex_proxy_unlock()` API delta，但沒有 GhostLock 的 `waiter->task`
   修補。

3. 公開 Android GhostLock implementations／target profiles 目前沒有
   `KFTRWI`、`trona`、`MT8183`、`PS7330` 或 `PS7331` exact target。既有
   `mtk-su64` payload 也已在本機 exact build 的 critical init step 3 失敗；
   不把相同 payload 重跑當作新證據。

4. 本輪沒有改變裝置。最後只讀 post-check 仍為 PS7330、ADB `device`、HOME
   Fire Launcher priority 50。

5. 官方 PS7331 source archive 確實包含 build script 指定的
   `kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig`。該
   source member 為 14,743 bytes，SHA-256 為
   `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac`。
   它是 Kconfig 的輸入檔，不是 signed kernel Image；其中未列出的
   `CONFIG_FUTEX`／`CONFIG_RT_MUTEXES` 不能被解讀為關閉。

6. 2026-08-04T03:26:32Z 的唯讀 postcheck 顯示裝置仍為 PS7330、ADB
   `device`、security patch `2024-02-01`，Fire Launcher 位於
   `/system/priv-app`，HOME resolver 仍為 priority 50 的
   `com.amazon.firelauncher/.Launcher`，且該 Activity 仍是 resumed。

### 高可信推論

- PS7331 不是已證明的 GhostLock remediation；source semantics 與 signed
  Image pattern 互相支持這個判定。
- 目前沒有足夠 exact-target 證據把公開 POC 改成可歸因的 Fire HD 10 root
  測試。執行錯誤 profile 的預期結果是 crash／reboot／不可歸因失敗，不是
  有價值的 negative compatibility result。

### 待驗證

- exact PS7330 signed Image 的 `remove_waiter()` binary semantics；shell
  不能讀取已安裝 boot block。
- source tree 中 `rt_mutex_proxy_unlock()` 的 `proxy_owner` 參照是否由
  未保存的 build patch／generated input 修正；沒有執行 compiler，因此不
  把 source package consistency issue 解讀成 signed binary 結果。
- PS7331 source defconfig 經完整 Kconfig 展開後的所有派生值；本階段沒有
  執行 kernel build，也沒有把 partial defconfig 當成 final config。

### 已排除／不採用

- 將 PS7331 Android header `kernel_offset=0x800` 當作 runtime exploit offset。
- 將其他 MTK SoC、其他 kernel version 或 Android 17 target profile 套到
  MT8183／Android 9。
- 將 `CVE-2026-43503` 或未核對的 CVE 名稱當作 GhostLock。
- 把 source-level PI 路徑存在寫成「已取得 root」。

### 因風險拒絕測試

- futex PI race、GhostLock reproducer、kernel memory access、native root
  payload、未知 ioctl、BROM／DA、preloader／LK、fastboot flash／unlock、
  boot／userdata／system 分割區寫入。

## 可重產檢查

```sh
python3 tools/scripts/check_phase5_ghostlock_source_semantics.py --dry-run \
  --source artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c \
  --output artifacts/phase5/ghostlock-source-semantics-20260804-01/mt8183.json
```

實際輸出：

- `mt8183.json` SHA-256 `3a02f57d3aeb548948666d7feda4e9121cdc3dff67998f637db6257e67225ba2`
- `legacy.json` SHA-256 `16edbad42503398ac7f683817ac0c5370592ce550f3b5aa53aa93171961d0f85`
- checker SHA-256 `9dd218d7d3f86288ea045edf72f4efecb7096d8b3daf7a3fdbe2f31237601503`

這個 checker 只讀 source、找出函式範圍與語意 pattern；它不執行 source、
不編譯、不讀取 device node、不計算地址，也不產生 payload。

## 目前最有價值的下一步

`trona_defconfig` 已抽出並與 PS7331 boot 內嵌 IKCONFIG 及 PS7330 live config
完成 focus-key provenance 比對。PS7330 與 PS7331 final-config evidence 的
focus keys 相同；defconfig 只作 build-input 佐證。無論結果如何，它不會
改變目前「PS7331 未證明修補 GhostLock」的判定，也不構成升級或 live root
測試授權。

## PS7331 source/config provenance

| Evidence | Observation | Classification |
|---|---|---|
| `artifacts/phase5/exact-kernel-source-review-7331-trona-defconfig-member-20260804-01/metadata.tsv` | Official source archive contains the exact `trona_defconfig` member selected by the build script | 已證實，source scope |
| `trona_defconfig:18,22,139–140,463–464,505` | Explicit `PREEMPT`, `RANDOMIZE_BASE`, MTK CMDQ, ION/MTK_ION and panic-on-oops selections | 已證實，source/config scope |
| `artifacts/phase5/phase5bc-defconfig-focus-20260804-01/summary.json` | PS7330 live and PS7331 boot-embedded focus keys compare equal; defconfig is not treated as a final-image dump | 已證實，provenance scope |

The build-selected `rtmutex.c` source member still does not contain a
`waiter->task` GhostLock fix. Its semantics checker remains the stronger
source-level indicator for this question, while the PS7331 reconstructed signed
Image review remains the binary-level evidence. Neither justifies writing the
standalone `boot.img` to the device.
