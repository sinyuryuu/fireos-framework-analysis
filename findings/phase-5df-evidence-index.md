# Phase 5DF evidence index

所有 evidence 均為主機端、唯讀的 PS7331 source audit；未接觸裝置，未執行
source/native object，未呼叫 futex 或 kernel memory API。

| Evidence ID | Source | File | SHA-256 | Command / scope | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|---|---|
| P5DF-001 | Official PS7331 source | `platform/kernel/mediatek/mt8183/4.4/kernel/futex.c` | See `summary.json` | Static landmark scan | syscall dispatch contains WAIT_REQUEUE_PI/CMP_REQUEUE_PI and proxy requeue path | Kernel source reachability boundary exists | Confirmed |
| P5DF-002 | Official PS7331 source | `platform/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | See `summary.json` | Static landmark scan | proxy start, `ret` cleanup, early self-deadlock return, waiter assignment and current cleanup are present | Pre-fix semantic landmarks are present in source | Confirmed |
| P5DF-003 | Reproducible host script | `tools/scripts/audit_phase5df_futex_dispatch_boundary.py` | Recorded by Git | `python3 ... --kernel-root ... --output ...` | Emits CSV, JSON and SHA manifest without device contact | Result is reproducible and bounded | Confirmed |
| P5DF-004 | Generated artifact | `artifacts/phase5/phase5df-futex-dispatch-boundary-20260804-01/` | `sha256sums.txt` | 16 landmark classes | Source dispatch/dataflow landmarks are enumerated | Presence evidence only; no runtime claim | Confirmed |
| P5DF-005 | Phase 5DD/5DE cross-check | `findings/phase-5dd-native-futex-surface.md`, `findings/phase-5de-userspace-futex-source.md` | Public commit | Native marker and non-kernel source audits | No named requeue-PI caller in preserved inputs | Bounded negative observation; missing/indirect caller remains possible | Strong evidence |

## Confidence vocabulary

本索引只使用 `Confirmed`、`Strong evidence`、`Probable`、`Hypothesis`、
`Disproved`。`P5DF-004` 的 artifact manifest 是該目錄內輸出的 hash；輸入
source hash 同時保存在 `summary.json`。
