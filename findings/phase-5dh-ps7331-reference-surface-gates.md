# Phase 5DH — PS7331 reference-surface prerequisite gates

日期：2026-08-04

本輪只讀取保存的 PS7331 IKCONFIG 與 exact MT8183 source，對照
Phase 5DG reference architecture 的通用表面。沒有編譯、執行、提取
offset、呼叫 syscall、讀寫 kernel memory 或接觸裝置。

## IKCONFIG evidence

來源：

artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config

SHA-256：eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04

已保存的明確設定：

| Symbol | Value | Meaning |
|---|---|---|
| CONFIG_FUTEX | y | futex core enabled |
| CONFIG_RT_MUTEXES | y | rtmutex support enabled |
| CONFIG_CONFIGFS_FS | y | configfs support enabled |
| CONFIG_SLUB | y | SLUB allocator selected |
| CONFIG_USERFAULTFD | not set | explicit disabled in extracted config |
| CONFIG_SECCOMP | y | seccomp enabled |
| CONFIG_SECCOMP_FILTER | y | seccomp filter enabled |
| CONFIG_RANDOMIZE_BASE | y | kernel base randomization enabled |

## Source surface

Exact source contains generic implementations or declarations matching:

- configfs;
- pipe buffer structures and operations;
- userfaultfd symbols;
- futex requeue-PI dispatch;
- rtmutex proxy-lock function.

完整計數、代表檔案與 hashes：

artifacts/phase5/phase5dh-ps7331-reference-surface-gates-20260804-01/

重現：

    python3 tools/scripts/audit_phase5dh_ps7331_reference_surfaces.py \
      --kernel-root firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4 \
      --config artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config \
      --output artifacts/phase5/phase5dh-ps7331-reference-surface-gates-REPLACE

## 判定

- **已證實：** PS7331 image config enables futex, rtmutex, configfs, SLUB,
  seccomp and base randomization; userfaultfd is explicitly not set.
- **高可信推論：** Generic configfs/pipe source presence does not reproduce
  the Emerald later memory primitive, which depends on target-specific layout,
  allocator behavior and runtime state.
- **待驗證：** Whether any Fire-exposed, permitted interface can produce a
  comparable post-trigger effect without additional privileges; no such
  interface has been established.
- **已排除／不支持：** Treating generic configfs, pipe, SLUB or userfaultfd
  source names as evidence of a usable kernel read/write primitive.
- **因風險拒絕測試：** probing these interfaces with crafted objects, ioctl,
  pipe-cache manipulation, configfs writes, futex races or root payloads.

這輪結果縮小了參考移植的判斷：PS7331 的通用 kernel components 並不等於
Emerald 的 target-specific exploit chain；目前仍缺少 runtime identity
mismatch 與後續可控 memory effect 兩個核心證據。
