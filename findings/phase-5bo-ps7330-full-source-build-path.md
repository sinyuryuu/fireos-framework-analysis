# Phase 5BO：PS7330 完整 source archive 與 build-selected kernel path

日期：2026-08-04
範圍：從官方 PS7330 source archive 確認 `mt8183/trona_defconfig` 實際選用的 kernel source，並與 PS7331 對照

## 結論

### 已證實

1. 官方 PS7330 source archive 已完整保存於本機，大小為 `2,588,816,416`
   bytes，SHA-256 為
   `569eca7321910b095f7af8905592f92e47610d302e6930fd27a6a5dee9593665`。
   Archive 來源是 Amazon 的 [Fire_HD10-7.3.3.0-20240730.tar.bz2](https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2)。
2. Outer archive 的 `platform.tar` 包含 exact build-selected path：
   `kernel/mediatek/mt8183/4.4/` 與
   `kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig`。
3. 從完整 archive 抽出的 PS7330 build-selected `rtmutex.c` SHA-256 是
   `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`；
   build-selected `futex.c` SHA-256 是
   `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`。
4. 這兩個 exact PS7330 build-selected source member，與既有 PS7331
   `mt8183/4.4` source member **逐 byte identical**。這比先前 generic
   `kernel/mediatek/4.4` member 的 source-family證據更精確。
5. Exact build-selected PS7330 `remove_waiter()`（lines 1079–1129）仍含
   `current->pi_blocked_on = NULL`，並把 `current` 傳給
   `rt_mutex_adjust_prio_chain()`；同一路徑的 `futex.c` 在
   `rt_mutex_start_proxy_lock()` 與 `FUTEX_WAIT_REQUEUE_PI`／
   `FUTEX_CMP_REQUEUE_PI` dispatch 中仍存在。
6. Exact build-selected PS7330 與 fixed reference 的 machine-readable marker
   比對結果為：PS7330 `PRE_FIX_CURRENT_TASK_CLEANUP`，fixed reference
   `FIXED_WAITER_TASK_CLEANUP`。
7. 完整 source-path comparison table 已保存於
   [`output/tables/phase5bo-source-path-comparison.csv`](../output/tables/phase5bo-source-path-comparison.csv)。

### 高可信推論

- PS7330 與 PS7331 的公開、build-selected source family 在 GhostLock 根因
  function 上相同；因此現有證據更強地支持「PS7331 source 沒有套用該上游
  `waiter->task` 修補」，但仍不能代替 signed binary proof。
- PS7330 generic `kernel/mediatek/4.4` source member 與 build-selected
  `mt8183/4.4` member 不是同一份檔案。Generic `rtmutex.c` 與 build-selected
  版本只有 `rt_mutex_proxy_unlock()` signature 的小差異；`futex.c` 也有
  vendor-specific 差異。今後 GhostLock source 結論應以 `mt8183/4.4` 為主。

### 待驗證

- Amazon 的 PS7330 signed kernel 是否由這份 build-selected source 直接建置，
  或在簽署前加入未公開 backport。
- PS7330 compiled Image 的 `remove_waiter()`、`task_struct` offset、KASLR
  與 Android post-exploitation 行為。

### 已排除

- 「generic `kernel/mediatek/4.4` member 就是唯一的 PS7330 build input」：
  完整 archive 顯示實際有 `mt8183/4.4` build path。
- 「PS7331 source 與 PS7330 只因產品相同而推測相同」：現在已取得 exact
  PS7330 full archive，兩個 build-selected member 已逐 byte 比對。
- 「source member identical 就等於 signed binary identical 或 root 可用」。

### 因風險拒絕測試

沒有執行 futex race、kernel exploit、root payload、未知 ioctl、BROM/DA、
fastboot、OTA、boot image、分割區或任何裝置狀態修改。

## Source evidence

| Evidence ID | File | Observation | Confidence |
|---|---|---|---|
| `P5BO-ARCHIVE-001` | `firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2` | Official archive size/hash verified | Confirmed, archive scope |
| `P5BO-EXTRACT-001` | `artifacts/phase5/ps7330-full-source-members-20260804-01/metadata.json` | Six allow-listed nested members extracted; none missing | Confirmed, source scope |
| `P5BO-RTMUTEX-001` | extracted `kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | Exact build-selected PS7330 hash and pre-fix markers | Confirmed, source scope |
| `P5BO-FUTEX-001` | extracted `kernel/mediatek/mt8183/4.4/kernel/futex.c` | PI requeue and proxy-lock call path present | Confirmed, source scope |
| `P5BO-CROSS-001` | `artifacts/phase5/phase5bo-exact-build-source-marker-20260804-01/summary.json` | Exact PS7330 and PS7331 source classification identical | Confirmed, host-only comparison |
| `P5BO-CONFIG-001` | extracted `.../arch/arm64/configs/trona_defconfig` | `CONFIG_PREEMPT=y`, `CONFIG_RANDOMIZE_BASE=y`, `CONFIG_MTK_CMDQ=y`, `CONFIG_ION=y`, `CONFIG_MTK_ION=y` | Confirmed, source config scope |
| `P5BO-DIFF-001` | `output/tables/phase5bo-source-path-comparison.csv` | Exact PS7330／PS7331 build-selected `rtmutex.c` and `futex.c` byte-identical | Confirmed, host-only diff |
| `P5BO-DEVICE-001` | `adb/phase5/PHASE5BO-DEVICE-POSTCHECK-20260804-01/` | Device remains PS7330, ADB `device`, green verified boot, enforcing SELinux, HOME Fire Launcher | Confirmed, read-only post-check |

## Upgrade decision

PS7331 remains a valid adjacent-version source/binary research reference, but
the new exact PS7330 build-selected source comparison does not create a reason
to install PS7331 for GhostLock. It remains a full OTA / system mutation rather
than a reversible standalone boot-image test. The installed device was not
updated.

## Reproduction

```sh
python3 tools/scripts/extract_phase5_ps7330_nested_members.py --dry-run \\
  --archive firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2 \\
  --output artifacts/phase5/ps7330-full-source-members-YYYYMMDD-NN

python3 tools/scripts/extract_phase5_ps7330_nested_members.py \\
  --archive firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2 \\
  --output artifacts/phase5/ps7330-full-source-members-YYYYMMDD-NN
```

The extractor is host-only, allow-listed, refuses output overwrite, and does
not execute extracted source.
