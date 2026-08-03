# Phase 5AP：PS7330 kernel symbol visibility

日期：2026-08-04
裝置：`KFTRWI` / `trona` / MT8183
Build：`PS7330.4104N/0030099376128`
Test ID：`PHASE5AP-KERNEL-SYMBOL-20260804-01`

## 結論

### 已證實

- ADB shell 身分仍是 UID 2000、`u:r:shell:s0`，kernel 是
  `4.4.146+`，裝置 fingerprint 未變更。
- shell 讀取 `/proc/kallsyms` 與 `/proc/sys/kernel/kptr_restrict` 都被拒絕：
  `Permission denied`。
- `/proc/sys/kernel/perf_event_paranoid` 可讀，值為 `3`。
- `cat /proc/modules` 與 `/proc/version` 可讀；本次沒有 device node、ioctl、
  futex、reboot、package 或設定變更。

### 高可信推論

目前 ADB shell 無法用 `/proc/kallsyms` 直接取得 PS7330 runtime symbol
addresses，因此不能由 shell 即時建立 GhostLock 的 kernel address profile。
這與先前 exact boot block pull 被拒絕的邊界一致：目前能取得的是 kernel
version/config/source-family 證據，不是可執行 exploit target。

### 待驗證

- system/root context 是否能讀取 `/proc/kallsyms`；本階段不提升權限、不修改
  SELinux、不執行 root payload，因此不測試。
- PS7330 signed kernel 是否對 `remove_waiter()` 做過 Amazon 私有 backport。

### 因風險拒絕測試

- 不以 `perf_event`、futex race、kernel pointer leak、未知 Binder、BROM/DA 或
  bootloader 操作繞過 procfs policy。

## Reproduction

```sh
bash tools/scripts/capture_phase5ap_kernel_symbol_surface.sh \
  --serial G001LT0511550CFT \
  --test-id PHASE5AP-KERNEL-SYMBOL-20260804-01 \
  --output adb/phase5/PHASE5AP-KERNEL-SYMBOL-20260804-01
```

Raw output 與每檔 SHA-256 位於：
`adb/phase5/PHASE5AP-KERNEL-SYMBOL-20260804-01/sha256sums.txt`。
