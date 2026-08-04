# Phase 6C：LAB_ONLY readiness audit

## Scope

本輪只檢查主機工具、PS7331 source tree 與保存的 kernel config。沒有安裝
工具、修改 source/config、編譯或啟動 kernel，也沒有產生或執行 futex、race、
panic、memory operation 或 root payload。

## Result

**Status: NOT_READY**

| Gate | Result |
|---|---|
| Required PS7331 source tree | Present |
| AArch64 source/config identity | `CONFIG_ARM64=y`, `CONFIG_MMU=y`, `CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y`, `CONFIG_SLUB=y` |
| KASLR | `CONFIG_RANDOMIZE_BASE=y` |
| KASAN | Not enabled |
| Debug symbols | `CONFIG_DEBUG_INFO` not enabled |
| `CONFIG_USERFAULTFD` | Not enabled |
| Host QEMU AArch64 | Missing |
| Host LLVM objdump/readelf | Missing in audit environment |
| Free space | Approximately 19.2 GB at audit time |

## Interpretation

- **已證實：** current host is not ready for a reproducible instrumented
  AArch64 lab boot; QEMU and debug/KASAN prerequisites are absent.
- **高可信推論：** building a debug/KASAN variant requires a separate Linux/
  AArch64 toolchain and an isolated host copy/config, not the stock tablet.
- **待驗證：** whether a future isolated lab can boot the exact vendor source
  sufficiently to observe source-level instrumentation.
- **因風險拒絕測試：** changing the tablet kernel, booting an unverified image,
  running requeue-PI or adapting the lab into a root exploit.

## Reproducible output

- Script: `tools/scripts/check_phase6c_lab_readiness.py`
- Artifact: `artifacts/phase6c/phase6c-readiness-20260804-01/`
- SHA-256 manifest: `sha256sums.txt`

This audit is a preparation result only. It does not establish runtime
identity mismatch or GhostLock exploitability.
