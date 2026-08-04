# Phase 5BO evidence index

| Evidence ID | Source | File | Observation | Confidence |
|---|---|---|---|---|
| `P5BO-ARCHIVE-001` | Amazon official source archive | `firmware/original/Fire_HD10-7.3.3.0-20240730.tar.bz2` | 2,588,816,416 bytes; SHA-256 `569eca7321910b095f7af8905592f92e47610d302e6930fd27a6a5dee9593665` | Confirmed, archive scope |
| `P5BO-EXTRACT-001` | host-only nested extractor | `artifacts/phase5/ps7330-full-source-members-20260804-01/metadata.json` | Six selected members extracted, zero missing | Confirmed, source scope |
| `P5BO-RTMUTEX-001` | exact PS7330 build path | `artifacts/phase5/ps7330-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | SHA `6cb544…`; `current` cleanup marker remains | Confirmed, source scope |
| `P5BO-FUTEX-001` | exact PS7330 build path | `artifacts/phase5/ps7330-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c` | SHA `ca9140…`; PI requeue/proxy path present | Confirmed, source scope |
| `P5BO-CROSS-001` | exact PS7330 vs PS7331 comparison | `artifacts/phase5/phase5bo-exact-build-source-marker-20260804-01/summary.json` | Both pre-fix; fixed reference waiter-task | Confirmed, host-only |
| `P5BO-CONFIG-001` | exact `trona_defconfig` | `artifacts/phase5/ps7330-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig` | build path/config identity | Confirmed, source config scope |
| `P5BO-BOOT-001` | exact-device read-only probe | `adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/boot_pull.stderr.txt` | Signed PS7330 boot read denied | Confirmed, access scope |

This index does not prove signed-binary equivalence, runtime offsets, or root.

