# Phase 5BP：PS7330 build script 與 source-to-build provenance

日期：2026-08-04
範圍：僅分析 Amazon 官方 PS7330 source archive 中的 kernel build script；不
執行 build、不產生 boot image、不接觸裝置。

## Executive result

### 已證實

1. 官方 PS7330 archive 的 build configuration 選用實際的
   `kernel/mediatek/mt8183/4.4` subtree，而不是較泛化的
   `kernel/mediatek/4.4` 路徑。它同時選用 `trona_defconfig`、`arm64` 與
   `Image`/`Image.gz`/`Image.gz-dtb` 輸出（`P5BP-SCRIPT-001`）。
2. Script 指向 Android AOSP GCC prebuilt repository 的
   `llvm-r383902b` branch，並要求使用者另外提供 Clang 6.0.2/4691093
   相容編譯器（`P5BP-SCRIPT-002`）。
3. `build_kernel.sh` 會先執行 `trona_defconfig`，再以
   `CROSS_COMPILE`、`CLANG_TRIPLE` 與 `CC` 參數進行 kernel build，最後
   複製並檢查 arm64 boot output（`P5BP-SCRIPT-003`）。
4. 對兩個保存的 script 做靜態 token scan，沒有發現可執行的 patch、
   `git apply`、`git am`、`git cherry-pick`、overlay 或簽署命令
   （`P5BP-SCAN-001`）。

### 高可信推論

- 這組 script 支持「PS7330 公開 source 可用 exact trona/MT8183 kernel
  path 建構」的 provenance，但只涵蓋 source selection、toolchain selection
  與 kernel output。它不能單獨證明 Amazon 的 signed production boot image
  沒有在 script 外部套用 backport、CI patch、packaging 或 AVB signing。
- 由於 exact PS7330 `mt8183/4.4` 的 `rtmutex.c`/`futex.c` 已與 PS7331
  對應 source member byte-identical 且仍為 pre-fix marker，現有證據不支持
  「升級到 PS7331 即可因 GhostLock source 修補而獲得安全差異」；但 signed
  binary 仍未被直接讀取，不能把 source 結論升格為 binary 結論
  （`P5BO-CROSS-001`、`P5BO-BOOT-001`）。

### 待驗證

- Amazon release CI 是否在這些 script 之外套用 kernel patch。
- 7.3.3.0 signed boot image 的實際 `remove_waiter()` machine code 是否
  仍對應公開 source。
- PS7331 signed boot image 是否與公開 PS7331 source 有任何未反映在
  source archive 的 release-only差異。

### 已排除

- 「PS7330 完全沒有公開 kernel source」：完整官方 archive 已保存並能
  解析 exact build-selected path。
- 「generic `kernel/mediatek/4.4` member 必然是 trona build input」：
  build script 與 `trona_defconfig` 明確選用 `mt8183/4.4`。

### 因風險拒絕測試

沒有執行 script，因為它會 clone toolchain、呼叫 `make`、產生 kernel
image，且分析目標是 source provenance 而非建立可刷入 artifact。沒有執行
OTA、fastboot、bootloader、root exploit、未知 ioctl、partition write 或
任何可能改變裝置啟動狀態的操作。

## 來源與雜湊

| Evidence ID | Source | Observation | Confidence |
|---|---|---|---|
| `P5BP-ARCHIVE-001` | `firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2` | Official archive SHA-256 `569eca7321910b095f7af8905592f92e47610d302e6930fd27a6a5dee9593665` | 已證實（archive scope） |
| `P5BP-SCRIPT-001` | `artifacts/phase5/ps7330-build-scripts-20260804-01/build_kernel_config.sh:9–18` | Exact kernel path, defconfig, arch and image list | 已證實 |
| `P5BP-SCRIPT-002` | `.../build_kernel_config.sh:12–24` | Toolchain repo/branch/prefix and Clang recommendation | 已證實 |
| `P5BP-SCRIPT-003` | `.../build_kernel.sh:130–185` | Defconfig, full make, output copy and validation | 已證實 |
| `P5BP-SCAN-001` | `artifacts/phase5/ps7330-build-scripts-20260804-01/commands.txt` | No visible executable patch/overlay/signing step in the two files | 已證實（scan scope） |
| `P5BO-CROSS-001` | `artifacts/phase5/phase5bo-exact-build-source-marker-20260804-01/summary.json` | PS7330/PS7331 exact build-selected markers both pre-fix | 已證實（source scope） |
| `P5BO-BOOT-001` | `adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/boot_pull.stderr.txt` | Exact PS7330 boot read returned permission denied | 已證實（access scope） |

## Upgrade assessment

PS7331 remains a useful adjacent-version reference because an official OTA and
boot artifact are locally preserved. It is not a safe GhostLock validation
shortcut: installing it is a full device-state/boot-chain change, and the
current public source comparison does not show the expected `waiter->task`
fix. The responsible next step is to preserve the version-mismatch boundary,
not to flash or sideload the image.

## Reproduction

```sh
python3 tools/scripts/extract_phase5_ps7330_nested_members.py --dry-run \
  --archive firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2 \
  --output artifacts/phase5/ps7330-full-source-members-YYYYMMDD-NN

python3 tools/scripts/analyze_phase5bp_build_scripts.py \
  --scripts-dir artifacts/phase5/ps7330-build-scripts-20260804-01 \
  --output output/tables/phase5bp-build-script-controls.csv
```

The analyzer is host-only and does not execute the captured shell scripts.
