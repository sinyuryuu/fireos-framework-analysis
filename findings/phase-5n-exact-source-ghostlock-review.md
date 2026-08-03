# Phase 5N — exact public kernel source, GhostLock, and MTK surface review

## Executive result

這一輪把 Amazon 公開的 Fire HD 10 11th generation / Fire OS 7.3.3.0
source archive 尾端取樣，並抽出其中的 exact `kernel/locking/rtmutex.c`。
結果如下：

- **已證實（source scope）：** source member 的 SHA-256 是
  `c4ddac5fe820c7f07670bc332425be05b0df0400ae334a147b483f0ee9b07345`，與
  已保存的 Linux stable v4.4.146 `rtmutex.c` 快照完全相同。
- **已證實（source scope）：** `remove_waiter()` 在行 1079–1090 的舊邏輯
  會清除 `current->pi_blocked_on`；`rt_mutex_start_proxy_lock()` 在 proxy
  rollback error path 會呼叫它（行 1657–1689）。這正是 NebuSec 所描述的
  GhostLock/CVE-2026-43499 source-level pattern。
- **已證實（device config + source scope）：** captured device config 開啟
  `CONFIG_FUTEX=y`、`CONFIG_RT_MUTEXES=y`；exact `futex.c` 內仍有
  `FUTEX_WAIT_REQUEUE_PI`、`FUTEX_CMP_REQUEUE_PI` 與 proxy-lock 呼叫路徑。
- **已證實（compile-time scope）：** public source/config 可計算
  `struct rt_mutex_waiter` 的 AArch64 非 debug layout：`task=0x30`、
  `lock=0x38`、`prio=0x40`、`sizeof=0x48`。
- **高可信推論：** 如果已安裝的 PS7330 kernel 是由這份 source tree 建置，
  且沒有未公開的 backport，GhostLock 的根因很可能仍存在於已安裝 kernel
  的對應 source path。
- **待驗證：** source archive 並非 signed `boot.img`、`Image` 或 `vmlinux`；
  因此尚不能確認 Amazon 編譯出的 PS7330 binary 沒有私有 patch，也不能由
  source 計算 KASLR、kernel symbol、`task_struct.pi_blocked_on` 的編譯後
  offset、CPU entry area 或 gadget address。
- **因風險拒絕測試：** 沒有編譯、推送、觸發 GhostLock/ION/CMDQ、開啟
  `/dev/ion`、送 ioctl、取得 root、讀寫 boot/partition，或執行任何 BROM/
  DA/fastboot 操作。

## 1. Device and source provenance

| 項目 | 值 |
|---|---|
| Serial | `G001LT0511550CFT` |
| Model / product | `KFTRWI` / `trona` |
| Installed build | `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys` |
| Fire OS | `7.3.3.0` |
| Kernel | `Linux 4.4.146+`, arm64 |
| Source archive | `Fire_HD10-7.3.3.0-20240730.tar.bz2` |
| Archive length | `2,588,816,416` bytes |
| Archive ETag | `c14e143433d91648afe4634c30a35320` |

The archive is the official Amazon S3 source link listed for the Fire HD 10
11th generation: [Fire_HD10-7.3.3.0-20240730.tar.bz2](https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2).
The bounded range/recovery metadata and member hashes are in
[`artifacts/phase5/exact-kernel-source-review-20260804-02/`](../artifacts/phase5/exact-kernel-source-review-20260804-02/).
The public research article is [NebuSec IonStack Part II / GhostLock](https://nebusec.ai/research/ionstack-part-2/).
The CVE record is [NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499).

The source archive is version-aligned at the Fire OS marketing/build family
level, but that is not cryptographic proof that every source member was used to
produce the installed signed kernel.

## 2. Exact `rtmutex.c` comparison

The second bounded range was bytes `2535000000–2588816415` of the official
archive. `bzip2recover` recovered 319 independently decompressible blocks; the
reconstructed decompressed slice has SHA-256
`106e4b410b466164c75bd33d4467866ba6adc0fa0e8e0bd7e01c16bff4b621ac`.

The exact member is:

| Member | Recovered-slice offset | Bytes | SHA-256 |
|---|---:|---:|---|
| `kernel/mediatek/4.4/kernel/locking/rtmutex.c` | `165080564` | `46859` | `c4ddac5fe820c7f07670bc332425be05b0df0400ae334a147b483f0ee9b07345` |

The normalized 1,754-line content is byte-for-byte identical to the local
Linux stable v4.4.146 snapshot at
`artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v4.4.146.c`.
This is stronger than a string match: both normalized files have the same
SHA-256 and the host comparison produced zero diff lines.

Relevant source locations:

| Location | Observation | Classification |
|---|---|---|
| `rtmutex.c:1079–1090` | `remove_waiter()` uses `current->pi_lock`, dequeues the waiter, and clears `current->pi_blocked_on` | **已證實（source scope）** |
| `rtmutex.c:1657–1689` | `rt_mutex_start_proxy_lock()` starts proxy acquisition and calls `remove_waiter()` after an error | **已證實（source scope）** |
| `rtmutex_common.h:25–36` | waiter object is stack-oriented and contains two rb nodes, task, lock and priority fields | **已證實（source scope）** |

This establishes source overlap with the root-cause pattern. It does not
establish the runtime exploit chain on this arm64 Android tablet.

## 3. Futex PI reachability in the source/config model

The exact `kernel/mediatek/4.4/kernel/futex.c` member is 91,328 bytes with
SHA-256 `e4ff0f8cfc46d023f66b3e842e275ee9eb6725ac6902942e235af32d8f0a2ab5`.
The sampled source contains:

- `rt_mutex_start_proxy_lock()` at the PI requeue path;
- `rt_mutex_finish_proxy_lock()` at the waiter completion path;
- `FUTEX_WAIT_REQUEUE_PI` and `FUTEX_CMP_REQUEUE_PI` operation cases.

The captured runtime config records `CONFIG_FUTEX=y` and `CONFIG_RT_MUTEXES=y`.
It does not contain a separate `CONFIG_FUTEX_PI` line. In this v4.4 source
snapshot, the PI operation code is visible in `futex.c` without a separately
observed `CONFIG_FUTEX_PI` guard. The precise final object-code reachability
still depends on the complete vendor build and signed image.

Therefore:

- **高可信推論：** the source/config combination has the required families of
  futex and rtmutex code for a source-level GhostLock review.
- **待驗證：** the installed binary's exact call graph, backport status, and
  Android/SELinux restrictions on the relevant syscalls.
- **已排除：** treating the absence of a literal `CONFIG_FUTEX_PI` line as
  proof that PI support is disabled.

## 4. Source-derived offsets

The exact `rtmutex_common.h` member hash is
`ee7fcb3d8edb06312606073f02435da8e6bb1d60b53604733a218c75c48ec51c`, matching
the pinned v4.4.146 schema. With the captured AArch64 config and
`CONFIG_DEBUG_RT_MUTEXES` disabled, the reproducible calculation is:

| Field | Offset | Size |
|---|---:|---:|
| `tree_entry` | `0x00` | `0x18` |
| `pi_tree_entry` | `0x18` | `0x18` |
| `task` | `0x30` | `0x08` |
| `lock` | `0x38` | `0x08` |
| `prio` | `0x40` | `0x04` |
| `sizeof(struct rt_mutex_waiter)` | — | `0x48` |

The generated output is
[`artifacts/phase5/exact-source-layout-review-20260804-01/layout.json`](../artifacts/phase5/exact-source-layout-review-20260804-01/layout.json).
It deliberately does not calculate:

- `task_struct.pi_blocked_on`'s compiled offset;
- kernel virtual addresses or KASLR slide;
- physical-map/CPU-entry-area addresses;
- compiler-generated gadget addresses;
- an exploit header or payload.

Thus the answer to “公開內核源碼能不能算出 offset” is **可以，但只限
source/ABI compile-time layout**。它不能單獨產生這台裝置可用的 runtime
root exploit offset。

## 5. MT8183 configuration and ION cross-check

The exact MT8183 ARM64 defconfig member is 128,562 bytes with SHA-256
`55f430e2656d5e85d8f88a0810a71356408dba7f656b72739c2f099daf502426`.
Relevant entries include:

| Config/source fact | Evidence | Interpretation |
|---|---|---|
| `CONFIG_ARM64=y`, `CONFIG_ARM64_4K_PAGES=y`, `CONFIG_ARM64_VA_BITS_39=y` | `mt8183_defconfig:5,350–355` | Source ABI is arm64/4K/39-bit VA model |
| `CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y`, `CONFIG_PREEMPT=y` | `mt8183_defconfig:169,249,363` and captured runtime config | Matches the rtmutex/futex source review |
| `CONFIG_RANDOMIZE_BASE=y` | `mt8183_defconfig:436` and captured runtime config | Runtime addresses cannot be inferred from source alone |
| `CONFIG_ION=y`, `CONFIG_MTK_ION=y` | `mt8183_defconfig:3672–3675` and captured runtime config | ION is built into the source/config model |
| `CONFIG_MTK_CMDQ=y` | `mt8183_defconfig:1253` | CMDQ source is present; the earlier tested v2 request returned `-ENOTTY` on the v3 path |
| `# CONFIG_MTK_ENABLE_GENIEZONE is not set` | `mt8183_defconfig:2605` | GenieZone source presence does not prove this product enables the feature |

The exact ION source confirms the following control flow:

- `ion.c:1659–1664` registers `unlocked_ioctl=ion_ioctl` and
  `compat_ioctl=compat_ion_ioctl`;
- `ion.c:1593–1601` sends `ION_IOC_CUSTOM` to the driver callback;
- `ion_drv.c:612` creates the ION device with `ion_custom_ioctl`;
- `ion_drv.c:319–405` copies user data, resolves a handle, and implements an
  `ION_SYS_GET_PHYS` branch;
- no `capable()` call is visible in that function. This is an attack-surface
  observation, not proof of arbitrary read/write or privilege escalation.

The earlier read-only device inventory recorded `/dev/ion` with a permissive
Unix mode but SELinux enforcing. No new `open`, allocation, custom command,
physical-address request, DMA/cache request, malformed structure, or ioctl was
sent in this review.

## 6. CVE identifier boundary

GhostLock in the cited research is **CVE-2026-43499**. `CVE-2026-43503` is a
separate Linux kernel issue and must not be used as a GhostLock identifier. A
matching kernel version alone is not enough to claim applicability to either
issue; each needs its own source path, configuration, patch and runtime
reachability evidence.

## 7. Safety and next decision

No device state changed. The current evidence supports one additional static
analysis step—obtain or reconstruct the complete exact PS7330 kernel build
inputs and compare the signed kernel's `rtmutex` implementation—but does not
justify a live root attempt.

Any future live exploit, kernel trigger, ION ioctl, boot image extraction via
bootloader/BROM/DA, or partition operation is a separate high-risk operation.
It requires an operation-specific Level 3 report with exact target, image,
rollback and recovery details; this source review does not authorize it.
