# Phase 5O evidence index

| Evidence ID | Source / file | Observed result | Interpretation | Confidence |
|---|---|---|---|---|
| P5O-FUTEX-001 | `artifacts/phase5/exact-futex-sched-review-20260804-04/futex-comparison.json` | Exact `futex.c` 3341 lines vs upstream 3337; 27 diff lines / 3 hunks | Only three MTK FPSGO timer-hook additions were observed in the full comparison | 已證實（source scope） |
| P5O-FUTEX-002 | `.../futex-diff.txt` | No diff hunk around PI requeue/proxy operations | No source-level vendor change was observed there; binary status remains unknown | 高可信推論 |
| P5O-SCHED-001 | `.../sched-comparison.json` | Exact `sched.h` 3798 lines vs upstream 3224; 966 diff lines / 48 hunks | Vendor/Android scheduler structure differs materially | 已證實（source scope） |
| P5O-SCHED-002 | `.../sched-comparison.json` | `task_struct` line 1685; `pi_blocked_on` line 1945; WALT/CPU_FREQ_TIMES/SWAP markers precede or affect layout | Upstream-only task offset calculation is unsafe | 已證實（source scope） |
| P5O-CONFIG-001 | `.../kconfig-observations.tsv`; `adb/phase5/PHASE5F-CMDQ-RUNTIME-20260803-02/kernel_config.stdout.txt` | `CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y`, `CONFIG_DEBUG_RT_MUTEXES=n`; no literal `CONFIG_FUTEX_PI` | PI source family is enabled in the captured model; symbol naming differs in old tree | 已證實（config scope） |
| P5O-LAYOUT-001 | `artifacts/phase5/exact-source-layout-review-20260804-01/layout.json` | `rt_mutex_waiter`: task `0x30`, lock `0x38`, prio `0x40`, size `0x48` | Source/ABI layout is reproducible, but not a runtime exploit target | 已證實（source/ABI scope） |
| P5O-ANDROID-001 | `artifacts/phase5/android-public-poc-review-20260804-01/repo-metadata.tsv`; [CakesTwix detector](https://github.com/CakesTwix/Android-CVE-2026-43499) | Android detector has native ABI libraries and warns of crash/reboot | Useful for implementation study only; not installed | 已證實（public-source scope） |
| P5O-ANDROID-002 | same metadata; [Aristotle port](https://github.com/soralis0912/CVE-2026-43499-aristotle) | MediaTek Android 12 / 5.10.136 target, static-only status | Closest methodology, not a KFTRWI target | 已證實（public-source scope） |
| P5O-ANDROID-003 | same metadata; [target generator](https://github.com/xianwan1314/CVE-2026-43499-Poc-Analysis) | Requires exact boot/profile-driven target generation | Confirms public ports are not universal | 已證實（public-source scope） |
| P5O-ANDROID-004 | same metadata; Samsung/OnePlus/OPPO/Xiaomi ports | Per-device profiles and compiler-sensitive stack assumptions | Constants cannot be reused across SoC/kernel/build | 高可信推論 |
| P5O-ANDROID-005 | GitHub API repository search captured 2026-08-04 | Reviewed result set has no KFTRWI/trona/MT8183 profile | Search-scope absence, not global proof | 待驗證 |
| P5O-CVE-001 | `findings/phase-5n-exact-source-ghostlock-review.md`; NebuSec article | GhostLock is CVE-2026-43499; CVE-2026-43503 is separate | Prevents mixing unrelated kernel bugs | 已證實 |
| P5O-SAFETY-001 | `artifacts/phase5/exact-futex-sched-review-20260804-04/commands.txt`; public review commands | Host-only; no ADB, compiler, exploit, ioctl, fastboot or partition operation | Device state unchanged in this round | 已證實 |

## Remaining unknowns

- Whether the signed PS7330 kernel contains a private GhostLock backport.
- The compiled `task_struct.pi_blocked_on` offset and pselect stack placement.
- Whether the relevant syscall path is reachable from the tested Android SELinux
  domain.
- Whether a future public repository publishes an exact trona/MT8183 target.
