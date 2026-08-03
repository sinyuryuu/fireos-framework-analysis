# Phase 5AN evidence index — GhostLock exact target gate

| Evidence ID | Source | File / reference | Result | Confidence |
|---|---|---|---|---|
| `P5AN-001` | Public GhostLock technical description | [NebuSec IonStack Part II](https://nebusec.ai/research/ionstack-part-2/) | `remove_waiter` proxy rollback bug in futex PI/rtmutex; public affected range and trigger family | 強證據，external technical scope |
| `P5AN-002` | Exact Amazon source comparison | `findings/phase-5n-exact-source-ghostlock-review.md`; `artifacts/phase5/exact-kernel-source-review-20260804-02/rtmutex-comparison.json` | normalized exact `rtmutex.c` equals stable v4.4.146; old `current->pi_blocked_on` pattern | 已證實，source scope |
| `P5AN-003` | Exact futex/scheduler/config review | `artifacts/phase5/exact-futex-sched-review-20260804-04/summary.json`; `findings/phase-5o-exact-futex-sched-review.md` | runtime `FUTEX=y`, `RT_MUTEXES=y`, `PREEMPT=y`, ARM64/4K/VA39/KASLR; no literal `CONFIG_FUTEX_PI` | 已證實，config scope |
| `P5AN-004` | Source/ABI layout | `artifacts/phase5/exact-source-layout-review-20260804-01/layout.json` | `rt_mutex_waiter`: `task=0x30`, `lock=0x38`, `prio=0x40`, size `0x48`; runtime addresses excluded | 已證實，source/ABI scope |
| `P5AN-005` | Exact boot metadata capture | `adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/` | boot symlink points to `mmcblk0p16`; shell pull failed with permission denied | 已證實，visibility scope |
| `P5AN-006` | Adjacent OTA boot image | `firmware/extracted/PS7331/boot.img`; SHA-256 `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` | Android bootimg, kernel address `0x40080000`, page size 2048; PS7331 mismatch | 已證實，version-mismatch scope |
| `P5AN-007` | Public target source | `artifacts/phase5/public-source-review/CyberMeowfia/commit.json`; selected target header | Public target header is Pixel `blazer`/Android 17 family; no `KFTRWI/trona/PS7330` profile | 已證實，bounded public-source scope |
| `P5AN-008` | Safety boundary | `findings/phase-5an-ghostlock-exact-target-review.md` | no live futex race, exploit, root stage, boot write, BROM/DA or partition write | 因風險拒絕測試 |

## Capture hashes

The raw boot metadata capture preserves per-file hashes in
`adb/phase5/PHASE5AN-BOOT-READONLY-20260804-02/sha256sums.txt`. The exact kernel/source
hashes remain in the Phase 5N/5O artifacts and are not replaced here.
