# Phase 5N evidence index

All evidence in this index is host-side or previously captured read-only
device evidence. Confidence labels are deliberately scoped to the evidence.

| Evidence ID | Source / command | File | Observed result | Interpretation | Confidence |
|---|---|---|---|---|---|
| P5N-SRC-001 | Amazon official Fire HD 10 7.3.3.0 source archive metadata | `findings/phase-5c-exact-source-and-loader-search.md`; `artifacts/phase5/exact-kernel-source-review-20260804-02/metadata.tsv` | Archive length 2,588,816,416, ETag `c14e143433d91648afe4634c30a35320` | Version-aligned public source provenance; not a signed boot artifact | 已證實（provenance scope） |
| P5N-SRC-002 | HTTP range + `bzip2recover` + bounded member parser | `artifacts/phase5/exact-kernel-source-review-20260804-02/metadata.tsv` | Range B and recovered slice hashes recorded; 319 recovered blocks | Exact source members can be independently hashed without storing full archive | 已證實 |
| P5N-RT-001 | Member extraction and line inspection | `artifacts/phase5/exact-kernel-source-review-20260804-02/source-member-index.tsv`; `source-observations.tsv` | Exact `rtmutex.c` contains `current->pi_blocked_on` cleanup and proxy rollback call | Amazon public source has the pre-fix GhostLock root-cause pattern | 已證實（source scope） |
| P5N-RT-002 | `compare_phase5_exact_rtmutex_source.py` against pinned stable v4.4.146 snapshot | `artifacts/phase5/exact-kernel-source-review-20260804-02/rtmutex-comparison.json`; `rtmutex-compare.txt` | Both normalized 1,754-line files hash to `c4ddac...`; zero diff lines | Exact sampled Amazon member is identical to upstream v4.4.146 `rtmutex.c` | 已證實（sampled source scope） |
| P5N-FUTEX-001 | `futex.c` member search and captured config | `artifacts/phase5/exact-kernel-source-review-20260804-02/source-observations.tsv`; `adb/phase5/PHASE5F-CMDQ-RUNTIME-20260803-02/kernel_config.stdout.txt` | PI requeue/proxy functions and operation cases are present; `CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y` | Source/config supports a strong applicability hypothesis, not binary proof | 高可信推論 |
| P5N-LAYOUT-001 | `calculate_phase5_rtmutex_source_layout.py` | `artifacts/phase5/exact-source-layout-review-20260804-01/layout.json` | `task=0x30`, `lock=0x38`, `prio=0x40`, size `0x48` | Compile-time source/ABI layout only | 已證實（source/ABI scope） |
| P5N-MTK-001 | Exact MT8183 defconfig and ION source extraction | `artifacts/phase5/exact-kernel-source-review-20260804-02/source-observations.tsv` | ION/MTK_ION/CMDQ enabled in defconfig; GenieZone enable not set; ION custom/GET_PHYS path present | MTK attack surfaces are identified for static review; no exploitability claim | 已證實（source scope） |
| P5N-MTK-002 | Prior approved read-only/runtime boundary | `findings/phase-5m-mtk-surface-and-candidate-review.md`; `findings/phase-5h-cmdq-ioctl-result.md` | `/dev/ion` inventory exists; prior CMDQ compatibility result was `-ENOTTY`; no new ioctl | No live ION/CMDQ trigger was performed | 已證實 |
| P5N-CVE-001 | NebuSec article and NVD record | `findings/phase-5n-exact-source-ghostlock-review.md` | GhostLock identifier is CVE-2026-43499; 43503 is separate | Prevents CVE conflation | 已證實（source attribution） |
| P5N-SAFETY-001 | Host command record | `artifacts/phase5/exact-kernel-source-review-20260804-02/commands.txt` | No ADB, fastboot, BROM, DA, ioctl, exploit, root or partition operation ran | Device remained unchanged | 已證實 |

## Open questions

1. Whether the signed PS7330 kernel binary contains a private backport that is
   not visible in the public source archive.
2. Whether all PI futex entry points are reachable under the installed Android
   SELinux/domain restrictions.
3. The compiled `task_struct` layout and runtime addresses. Public source alone
   cannot answer these.
4. Whether ION's permissive node mode is usable by the shell domain in the
   exact running policy; no ioctl test was performed.
