# Phase 5O — exact futex/scheduler source and public Android implementation review

## Executive result

本輪回答兩個問題：公開 kernel source 能否計算這台 Fire HD 10 的 GhostLock
相關 layout，以及 GitHub 是否已有可參考的 Android 實作。

- **已證實（source/config scope）：** Amazon exact `futex.c` 與 stable
  v4.4.146 的差異只有三個 MTK FPSGO timer-hook hunk；沒有看到
  `FUTEX_WAIT_REQUEUE_PI`、`FUTEX_CMP_REQUEUE_PI` 或 proxy-lock 邏輯被改寫。
- **已證實（source/config scope）：** exact source 的 `init/Kconfig` 以
  `CONFIG_FUTEX` 選取 `RT_MUTEXES`；exact source、defconfig 與已保存 runtime
  config 都沒有一個獨立的 literal `CONFIG_FUTEX_PI` 設定行。這不是 PI
  路徑不存在的證明，因為 v4.4 的 PI 操作本身位於 `futex.c`。
- **已證實（source scope）：** exact vendor `sched.h` 不是 upstream
  v4.4.146 的 byte-identical copy。`struct task_struct` 從 source line
  1685 開始，`pi_blocked_on` 位於 line 1945；其前方有 Android／MTK／WALT
  等條件式欄位。
- **已證實（source/ABI scope）：** 公開 source 可以重現
  `struct rt_mutex_waiter` 的條件式欄位 layout（本專案先前計算為
  `task=0x30`、`lock=0x38`、`prio=0x40`、size `0x48`）。
- **高可信推論：** 這份 exact source/config 與 GhostLock 根因相容，但還
  不能把 source layout 當成這台裝置可直接使用的 exploit target。
- **已證實（public implementation scope）：** GitHub 上的 Android ports
  都以 exact device／kernel／compiler layout 為中心；找到的 Android 12
  MediaTek port是另一個 MTK SoC、5.10 kernel，而且 README 明確標示尚未
  在硬體驗證。沒有找到可直接套用到 `KFTRWI/trona/MT8183/4.4.146` 的公開
  target profile。
- **因風險拒絕測試：** 沒有下載、編譯、安裝、推送或執行任何 Android
  root PoC、crash detector、native library 或 payload；沒有新的 ADB、
  fastboot、ioctl、kernel trigger 或分割區操作。

## 1. Exact source comparison

分析工具是
[`analyze_phase5_exact_futex_sched.py`](../tools/scripts/analyze_phase5_exact_futex_sched.py)，
輸出位於
[`artifacts/phase5/exact-futex-sched-review-20260804-04/`](../artifacts/phase5/exact-futex-sched-review-20260804-04/)。

### `futex.c`

| 項目 | Exact Amazon source | stable v4.4.146 | 結果 |
|---|---:|---:|---|
| normalized lines | 3341 | 3337 | 不同 |
| normalized SHA-256 | `e4ff0f8cfc46d023f66b3e842e275ee9eb6725ac6902942e235af32d8f0a2ab5` | `8a920516884f29a1e4e13ccfcd292e0307e4f0868ab9c520d4fff2b8c2751720` | 不同 |
| unified diff | 27 lines / 3 hunks | — | 只有 FPSGO timer additions |

實際差異為：

1. `#include <mt-plat/fpsgo_common.h>`；
2. `hrtimer_init_sleeper()` 後的 `xgf_igather_timer(&to->timer, 1)`；
3. cleanup path 的 `xgf_igather_timer(&to->timer, to->task ? -1 : 0)`。

這三處不在 GhostLock 的 proxy rollback／PI requeue 判斷附近。exact source
仍包含 `rt_mutex_start_proxy_lock()`、`rt_mutex_finish_proxy_lock()` 以及
`FUTEX_WAIT_REQUEUE_PI`／`FUTEX_CMP_REQUEUE_PI` cases。因此可說「source
中仍有相關路徑」，不能說「已證明 signed kernel 一定可被 exploit」。

### `sched.h`

| 項目 | Exact Amazon source | stable v4.4.146 |
|---|---:|---:|
| normalized lines | 3798 | 3224 |
| normalized SHA-256 | `fd3eb1c3dd015bf897dfe2b8d3b832b2c1f70b09c18e3d8b2a26391319121d9d` | `5c53697385a13578dea01c79c7a0ea6834740a4236e4828a2d8404d4dbddc00c` |
| unified diff | 966 lines / 48 hunks | — |
| `struct task_struct` definition | line 1685 | — |
| `pi_blocked_on` | line 1945 | — |

可見的條件式／vendor marker 包含 `CONFIG_THREAD_INFO_IN_TASK`、
`CONFIG_SCHED_WALT`、`CONFIG_CPU_FREQ_TIMES` 與 `CONFIG_SWAP`。因此公開
source 可以限制 ABI 模型，但不能只用 upstream `sched.h` 推出 Amazon
編譯後 `task_struct.pi_blocked_on` 的可靠 runtime offset。

## 2. Kconfig and runtime configuration

exact `kernel/mediatek/4.4/init/Kconfig` 的關鍵語意是：

```text
config FUTEX
    default y
    select RT_MUTEXES
```

exact MT8183 defconfig 與既有 runtime config 均記錄：

| Key | defconfig | runtime | Interpretation |
|---|---|---|---|
| `CONFIG_FUTEX` | `y` | `y` | futex enabled |
| `CONFIG_RT_MUTEXES` | `y` | `y` | rtmutex enabled |
| `CONFIG_DEBUG_RT_MUTEXES` | `n` | `n` | non-debug layout model |
| `CONFIG_PREEMPT` | `y` | `y` | preemptible kernel model |
| `CONFIG_THREAD_INFO_IN_TASK` | `y` | `y` | affects task layout |
| `CONFIG_SCHED_WALT` | `y` | `y` | vendor scheduler fields |
| `CONFIG_RANDOMIZE_BASE` | `y` | `y` | source cannot provide runtime addresses |
| `CONFIG_MTK_ION` | `y` | `y` | unrelated MTK ION surface is built |
| `CONFIG_MTK_ENABLE_GENIEZONE` | `n` | `n` | GenieZone source is not evidence of enabled product path |

`CONFIG_FUTEX_PI` 的 literal absence不能被寫成「PI disabled」；在這個 old
tree 中，PI operation cases 和 rtmutex proxy code 已由 `CONFIG_FUTEX`／
`RT_MUTEXES` 這組語意涵蓋。完整觀察在
[`kconfig-observations.tsv`](../artifacts/phase5/exact-futex-sched-review-20260804-04/kconfig-observations.tsv)。

## 3. What public source can and cannot calculate

### Can calculate

- `struct rt_mutex_waiter` 的 source/ABI field order and conditional size；
- exact source 是否含 `remove_waiter()` 舊 pattern；
- futex PI operation cases、rtmutex proxy call sites；
- selected config and vendor source additions；
- source-level comparison against a pinned 4.4.146 baseline。

### Cannot calculate from this source alone

- signed PS7330 `boot.img`／`Image`／`vmlinux` 是否含 private backport；
- compiler-generated `pselect` stack frame / waiter placement；
- compiled `task_struct.pi_blocked_on` offset；
- KASLR slide、physical linear-map address、CPU entry area、gadget address；
- Android SELinux domain reachability and exact syscall behavior；
- a working root payload。

NebuSec 的公開文章把 GhostLock 描述為 `remove_waiter()` proxy path 的問題，
但也把 Android adaptation 與 generic x86 discussion 分開；文章本身不是
KFTRWI target profile。參考：[IonStack Part II / GhostLock](https://nebusec.ai/research/ionstack-part-2/)。

## 4. Public Android implementation review

以下是以 pinned commit 及 README hash 保存的公開參考；完整 metadata 在
[`repo-metadata.tsv`](../artifacts/phase5/android-public-poc-review-20260804-01/repo-metadata.tsv)。

| Project | Android／kernel scope | 判定 | 對本機價值 |
|---|---|---|---|
| `CakesTwix/Android-CVE-2026-43499` | Android 7+ detector，arm64/armv7 native libraries | detector only | 可作「是否存在觸發跡象」的程式結構參考；README 明示可能 crash/reboot，未安裝 |
| `xianwan1314/CVE-2026-43499-Poc-Analysis` | boot/profile-driven generic arm64 target generator | exploit porting framework | 證明需要 exact boot/profile；不是通用 Android 9／MT8183 target，未編譯 |
| `soralis0912/CVE-2026-43499-aristotle` | MediaTek、Android 12、5.10.136、arm64 | closest methodology, not target | 需要重新取得 offset、KASLR／stack／phys-load；README 標示尚未硬體驗證 |
| `Wtrwx/smt878u-ionstack-poc` | Samsung、Android 13、4.19.113、arm64 | device-specific | profile fail-closed；與 Amazon SoC/build 不同 |
| `JoinChang/ghostlock-oneplus` | Android 16、6.6/6.12、compiler-sensitive stack layout | modern port study | 直接說明同 kernel version 也可能因 compiler/PGO layout 不同而不可移植 |
| `pubglite55/oppo-ghostlock` | OPPO、Android 16、5.10.236、arm64 | incomplete research port | 仍是另一個 vendor tree / compiler / target |
| `tc3650/CVE-2026-43499-armv7` | Android 12、5.4.161、armv7l | blocked architecture study | 其 README 說明 ARM32 的 PI chain 行為與 64-bit 路徑不同 |
| `MobiusM/CVE-2026-43499` | generic Android NDK/CMake | crash-oriented PoC | 沒有 exact device profile，不執行 |
| `Colorful-glassblock/duchamp-root` | MT6897、Android 16、6.1.138 | device-specific | MTK 只是 SoC vendor 相同，kernel generation 和 layout 完全不同 |

公開來源：[Android detector](https://github.com/CakesTwix/Android-CVE-2026-43499)、
[MediaTek Aristotle port](https://github.com/soralis0912/CVE-2026-43499-aristotle)、
[Samsung 4.19 port](https://github.com/Wtrwx/smt878u-ionstack-poc)、
[generic Android target generator](https://github.com/xianwan1314/CVE-2026-43499-Poc-Analysis)。

截至本次 pinned GitHub repository search，reviewed public profiles 沒有
`KFTRWI`、`trona`、`MT8183` 或 Fire OS 7.3.3.0 target。這是搜尋範圍內的
結果，不是對整個 GitHub 的絕對不存在證明。

## 5. Decision and safe next step

公開 kernel source **可以算出 source/ABI 層級的部分 layout**，也能讓我們
判斷 exact source 仍保留 GhostLock 的相關 futex/rtmutex family；但它不能
單獨生成這台裝置可用的 Android root POC。最小的下一個「仍屬靜態」目標是
取得與 `PS7330.4104N` 完全匹配的 signed kernel ELF／debug information，或
完成可重現的同版 kernel build，從而確認編譯後的 `task_struct` 與 stack
layout。這不等同於授權 live exploit。

任何把 detector／generic port 編譯後推到裝置、觸發 futex UAF、寫 kernel
memory、改 cred/SELinux、取得 root 或使用 bootloader/BROM/DA 的動作，都要
另立 operation-specific Level 3 report；本輪明確沒有執行。
