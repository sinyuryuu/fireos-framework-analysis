# Phase 5AN：GhostLock exact target gate 與 boot metadata review

日期：2026-08-04
裝置：Amazon Fire HD 10 2021，`KFTRWI` / `trona` / MT8183
Build：`Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys`
Kernel：`Linux 4.4.146+ #1 SMP PREEMPT Sat Jul 13 02:13:14 UTC 2024 aarch64`

## 結論先行

### 已證實

1. GhostLock 對應 `CVE-2026-43499`，根因在 Linux `kernel/locking/rtmutex.c` 的
   `remove_waiter()`：proxy-lock rollback 使用 `current` 而不是實際 waiter task。
   公開研究描述的 trigger family 是 `FUTEX_WAIT_REQUEUE_PI`／
   `FUTEX_CMP_REQUEUE_PI` 與 PI dependency cycle。[NebuSec technical write-up](https://nebusec.ai/research/ionstack-part-2/)
2. Amazon Fire OS 7.3.3.0 public source 中的 exact `rtmutex.c` normalized SHA-256
   `c4ddac5fe820c7f07670bc332425be05b0df0400ae334a147b483f0ee9b07345` 與 pinned
   Linux stable v4.4.146 reference 相同；source review 找到舊的
   `current->pi_blocked_on` pattern 與 proxy rollback caller。
3. exact runtime config 讀到 `CONFIG_FUTEX=y`、`CONFIG_RT_MUTEXES=y`、
   `CONFIG_PREEMPT=y`、`CONFIG_ARM64=y`、`CONFIG_ARM64_4K_PAGES=y`、
   `CONFIG_ARM64_VA_BITS_39=y`、`CONFIG_RANDOMIZE_BASE=y`、SELinux 與 seccomp。
   舊版 v4.4 tree 沒有獨立 literal `CONFIG_FUTEX_PI` 行；不能把該字串缺失解讀成
   PI 路徑不存在。
4. exact ADB shell 可以看見 boot symlink `/dev/block/by-name/boot ->
   /dev/block/mmcblk0p16`，但 `adb pull /dev/block/by-name/boot` 回傳
   `Permission denied`；本輪沒有取得、寫入或重啟 boot partition。
5. 工作區中唯一可解析的 `boot.img` 是相鄰的 PS7331 OTA，SHA-256
   `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`。它不是
   installed `PS7330.4104N`，不能作為 exact target 或 recovery input。

### 高可信推論

- 若 PS7330 signed kernel 是由已保存的 7.3.3.0 source tree 建置且沒有未公開
  backport，GhostLock root-cause pattern 很可能仍在 binary 對應路徑中；但這仍是
  source/config inference，不是 runtime vulnerable confirmation。
- 本機確實比公開 Pixel/Android 17 target 更接近 old-kernel source family，但
  public GhostLock exploit 需要 target-specific kernel profile：編譯後
  `task_struct`／stack layout、KASLR/physmap、CPU-entry-area、function-table
  address 與 SELinux/root stage。沒有 exact profile，直接執行會是 crash-prone
  blind test。

### 待驗證

- signed PS7330 `boot.img`／kernel ELF 是否含未公開 backport；目前 boot block
  讀取被 shell SELinux/permission boundary 阻擋。
- `task_struct.pi_blocked_on` 的 compiled offset、kernel virtual/physical layout、
  toolchain-generated gadgets 與 exact Android syscall policy。
- exact PS7330 是否能安全進入公開 reproducer 的 rollback path；目前沒有 live
  futex race 或 crash evidence。

### 已排除

- 把 source-derived `struct rt_mutex_waiter` layout（`task=0x30`、`lock=0x38`、
  `prio=0x40`、size `0x48`）當成完整 exploit target header。
- 把 PS7331 `boot.img`、Pixel `blazer` target header、其他 MTK SoC/Android build
  的 offsets 直接套用到 `trona/PS7330`。
- 把 `CVE-2026-43503`（skb/XFRM/ESP）或 `CVE-2026-3499`（WordPress CSRF）當成
  GhostLock。

### 因風險拒絕測試

- 不執行公開 GhostLock reproducer／root exploit、futex PI race、stack-UAF reclaim、
  kernel memory write、SELinux/credential modification 或 su daemon stage。
- 不讀寫 boot/raw block、BROM/DA/preloader/LK/seccfg，不解鎖 bootloader，不刷入
  PS7331 或其他版本 image。

## Exact source and runtime evidence

| Evidence | 位置 | 觀察 |
|---|---|---|
| `P5AN-001` | `findings/phase-5n-exact-source-ghostlock-review.md` | exact Amazon `rtmutex.c` 與 v4.4.146 reference 相同；舊 `remove_waiter` pattern |
| `P5AN-002` | `artifacts/phase5/exact-kernel-source-review-20260804-02/rtmutex-comparison.json` | normalized identical, source-only scope |
| `P5AN-003` | `artifacts/phase5/exact-futex-sched-review-20260804-04/summary.json` | runtime config and exact `futex.c` diff; vendor additions are FPSGO timer hooks outside the GhostLock hunk |
| `P5AN-004` | `artifacts/phase5/exact-source-layout-review-20260804-01/layout.json` | source/ABI-only waiter layout; explicitly excludes runtime offsets and addresses |
| `P5AN-005` | `adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/` | boot symlink visible; `adb pull` denied; exact boot not obtained |
| `P5AN-006` | `firmware/extracted/PS7331/boot.img` | adjacent PS7331 Android boot image; `file` reports kernel address `0x40080000`, page size 2048; version mismatch |
| `P5AN-007` | `artifacts/phase5/public-source-review/CyberMeowfia/` | pinned public source contains Pixel/other Android target profiles only; no `KFTRWI/trona/PS7330` profile |

## Public implementation review

The NebuSec page describes GhostLock as a local unprivileged Linux kernel issue and
publishes a reproducer/exploit split. The exploit source snapshot reviewed locally
contains target headers for Pixel `blazer` and other Android builds; the selected
`blazer` header identifies `google/blazer/blazer:17/CP2A.260605.012`, not this
Amazon fingerprint. The source was not compiled, pushed, installed or executed.

This matters because the public exploit's later stages are not just a futex call:
they depend on a kernel-stack reclamation strategy, compiled kernel addresses and a
root/SELinux stage. A source match proves the candidate family, not portability.

## Boot image and offset result

The requested exact boot extraction was attempted as a read-only ADB operation and
failed before any bytes were read:

```text
adb -s G001LT0511550CFT pull /dev/block/by-name/boot .../boot.raw
adb: error: failed to stat remote object '/dev/block/by-name/boot': Permission denied
```

Therefore the current result is:

| Requested item | Result |
|---|---|
| Exact PS7330 boot image | unavailable through shell ADB |
| Exact kernel ELF / signed Image | unavailable |
| Source/ABI waiter layout | available, `0x30/0x38/0x40`, size `0x48` |
| Runtime `task_struct.pi_blocked_on` offset | unavailable |
| Runtime KASLR/physmap/CEA/gadget offsets | unavailable |
| Device-specific GhostLock root target | not established |

## Decision

GhostLock is currently the strongest **source-level** candidate for this old ARM64
kernel, but not an executable exact-device root path. The most valuable next evidence
is a legally obtained exact PS7330 boot/kernel artifact or a reproducible matching
kernel build; until then, running the public Pixel/other-device exploit would not be a
meaningful compatibility test and could simply crash or corrupt the tablet.
