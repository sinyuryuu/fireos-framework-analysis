# Phase 5CO evidence index

本輪為主機端 source/config resolution，並引用先前已保存的 PS7331 read-only
runtime capture。沒有新增裝置狀態修改，沒有觸發 futex PI 或執行 exploit。

| Evidence ID | Source | File / location | SHA-256 | Observation | Confidence |
|---|---|---|---|---|---|
| `P5CO-SRC-001` | Official PS7331 source archive | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` | Exact source input used by the host-only extraction/search scripts | Confirmed |
| `P5CO-SRC-002` | Extracted Kconfig | `.../kernel/mediatek/4.4/init/Kconfig:1570-1585` | `80b895f9bbad97978823720c357f89e8835d6c0e48336c906c7d8693de3b2957` | Defines `FUTEX` and `HAVE_FUTEX_CMPXCHG`; FUTEX selects RT_MUTEXES | Confirmed, source scope |
| `P5CO-SRC-003` | Extracted MT8183 ARM64 header | `.../mt8183/4.4/arch/arm64/include/asm/futex.h:92-125` | `0aa4289efa3f2f045329969616c74430a4e088b16366f665ec1a0ced09ff3fdc` | Atomic cmpxchg implementation; invalid user address returns `-EFAULT` | Confirmed, source scope |
| `P5CO-SRC-004` | Extracted Linux futex header | `.../kernel/mediatek/4.4/include/linux/futex.h:58-65` | `441dee4eb544aefaafeeb3860b5cc1b6027464cdd22503499a3bd16fc246175b` | Symbol selects compile-time constant versus runtime variable | Confirmed, source scope |
| `P5CO-SEARCH-001` | Host-only literal search | `artifacts/phase5/phase5cn-futex-literal-search-20260804-01/metadata.json` | `6874274db40742228369292bd3a8d40e1661907ee14cbd71ecca72ee38a15fe8` | MT8183 ARM64 platform block has no direct select; MediaTek select found at MT8167 ARM Kconfig block | Confirmed search scope; not final `.config` proof |
| `P5CO-SRC-005` | Extracted MT8183 ARM64 platform Kconfig | `.../mt8183/4.4/arch/arm64/Kconfig.platforms:255-294` | `89ab399110832ccafe6e5905f02e7df88959f94a2f023406d40f90773cf1a93d` | `MACH_MT8183` block contains no `HAVE_FUTEX_CMPXCHG` select | Confirmed, source scope |
| `P5CO-BUILD-001` | Official PS7331 boot embedded IKCONFIG | `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config` | `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04` | FUTEX, RT_MUTEXES, PREEMPT, ARM64 and KALLSYMS are enabled; no line for HAVE_FUTEX_CMPXCHG | Confirmed image artifact; symbol absence is not alone a complete Kconfig proof |
| `P5CO-RUNTIME-001` | PS7331 device read-only capture | `adb/phase5/PS7331-CONFIG-GATES-20260804-03/config.stdout.txt` | `803ae046bd72a33481f8472591b11b29090561ac3f254a2772aaf9e0322d823d` | Device reports `CONFIG_FUTEX=y` and `CONFIG_RT_MUTEXES=y` | Confirmed runtime config |
| `P5CO-RUNTIME-002` | PS7331 status capture | `adb/phase5/PS7331-STATUS-20260804-02/result.md` and `sha256sums.txt` | `aa25ae611fd7c30987e205047d7bbb6667bc406208a31e10924c759fe04cf5c9` (`sha256sums.txt`) | Read-only capture; no device nodes opened, blocks read, payloads executed or device writes | Confirmed safety scope |
| `P5CO-D1-001` | Evidence audit | No captured identity trace | N/A | No observation of `waiter->task != current` | Confirmed unobserved |
| `P5CO-D2-001` | Evidence audit | No captured post-cleanup state trace | N/A | No proof of persistent invariant violation or memory effect | Confirmed unproven |

## Interpretation rule

`P5CO-SRC-*` proves source semantics only. `P5CO-BUILD-*` and
`P5CO-RUNTIME-*` prove feature presence/configuration only. None substitutes for a
same-execution D1 identity observation.
