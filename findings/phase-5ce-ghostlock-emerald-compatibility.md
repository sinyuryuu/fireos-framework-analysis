# Phase 5CE：GhostLock Emerald 公開實作相容性審查

日期：2026-08-04

範圍：公開 GitHub `datfooldive/ghostlock-emerald` 的 README、Makefile、
source tree 與 target metadata；與本專案保存的 Fire OS 7.3.3.1／PS7331
source 與 boot evidence 做 host-side 對照。沒有 clone、編譯、安裝、執行
該 exploit，也沒有裝置操作。

公開來源版本：`ebb355d302629a034d0959e5e579496559e8f84e`
（`main`，2026-08-04 讀取）。

## Executive verdict

### 已證實：這不是可直接套用到 Fire HD 10 的通用 POC

公開專案 README 將目標標為 Poco M6 Pro（MT6789）與 kernel
`6.12.30-android16-5-...`；Makefile 使用 Android NDK API 35、AArch64
cross-compiler，並把 `pipe_physrw.c`、`root.c`、`miniadb.c`、`umh_root.c`
等元件編入最終 binary。

其 `target.h` 明確包含 build fingerprint、kernel image/physical mapping、
task/credential/SELinux/pipe/fops 等 target layout metadata；target header
本身還帶有 `ghostlock_oneplus` build label。這類資料是特定 kernel build
的 profile，不是 Android API 或 SoC 無關的設定。

### 高可信推論：Fire PS7331 不能直接執行該 binary

本機目標是 Fire OS 7.3.3.1、Android 9、MT8183、4.4 系列 kernel；公開
Emerald profile 是 MT6789、Android 16、6.12.30。兩者在 kernel generation、
task/cred/rtmutex layout、物理映射、符號與 device profile 上均不相同。

因此即使 GhostLock 的 source-level defect family 相同，Emerald binary
仍不具備對 PS7331 的 target compatibility。直接安裝或執行不會是有效的
相容性測試，而是未驗證的 kernel memory/root payload。

### 因風險拒絕測試

以下操作本階段不執行：

- 下載後編譯或修改 Emerald exploit；
- sideload、`adb push` 後執行或以任何方式觸發 kernel race；
- 使用其 kernel physical-R/W、credential、SELinux 或 KernelSU 路徑；
- 以 MTK lower-layer、bootloader、fastboot、DA、preloader 或分割區寫入
  方式嘗試 root 或刻意造成變磚。

這些操作可能造成 kernel crash、資料損壞、永久失去 ADB 或不可逆 boot
狀態，且目前沒有 PS7331 target profile 或可驗證 rollback。

## Target comparison

| Dimension | Emerald public project | Fire PS7331 | Result |
|---|---|---|---|
| Device/SoC | Poco M6 Pro / MT6789 | Fire HD 10 / MT8183 | mismatch |
| Android/kernel | Android 16 / 6.12.30 | Android 9 / 4.4 family | mismatch |
| Build tool | NDK API 35 AArch64 | PS7331 vendor kernel build | mismatch |
| Target metadata | hard-coded build/layout profile | separate signed boot/source evidence | no shared profile |
| Root stage | project includes root/user-mode-helper components | not validated on Fire | unproven |
| Direct execution | not tested here | rejected | unsafe/invalid experiment |

## Relation to current PS7331 evidence

本專案 Phase 5CB–5CD 已確認的是：

- PS7331 source 有 futex syscall → PI requeue → proxy-lock source path；
- `current` 與 explicit waiter task 在 source interface 中可分離；
- `remove_waiter()` 的 cleanup target 與後續 consumer 已完成 source mapping。

仍未確認：

- Android userspace 是否能在此 build 形成 proxy waiter；
- runtime `current != waiter->task`；
- cleanup 後的持久狀態異常與第二次消費；
- crash、controlled memory effect 或 privilege transition。

所以 Emerald 專案只能作為 target-profile 架構參考，不能提升上述任一項
為 Fire OS runtime 證據。

## Safe research result

本階段沒有產生可執行 exploit、offset generator、kernel writer 或 APK。
後續仍可安全進行的工作限於：

1. 對 PS7331 exact source 做更完整的非執行式 call/data-flow review；
2. 比對官方 source、Image metadata 與既有 sanitized binary evidence；
3. 將 Emerald 的 target-profile 欄位抽象成不含 exploit payload 的相容性
   schema，證明 Fire profile 缺失哪些必要資料；
4. 將 source candidate 與 runtime/root proof 分開維持在報告中。

## Public sources

- [Emerald README](https://github.com/datfooldive/ghostlock-emerald/blob/main/README.md)
- [Emerald Makefile](https://github.com/datfooldive/ghostlock-emerald/blob/main/Makefile)
- [Emerald target.h](https://github.com/datfooldive/ghostlock-emerald/blob/main/src/core/target.h)
- [Emerald device metadata](https://github.com/datfooldive/ghostlock-emerald/blob/main/src/devices/emerald/offsets.h)
- [Emerald source tree](https://github.com/datfooldive/ghostlock-emerald/tree/main/src/core)
