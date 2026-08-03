# Phase 5P evidence index

本索引只收錄本輪新增的 Android port 靜態審查與唯讀 runtime gate。所有
confidence 使用本專案既有標籤：Confirmed、Strong evidence、Probable、
Hypothesis、Disproved。

## P5P-DEVICE-001

- Source: device read-only gate capture
- File: `adb/phase5/PHASE5P-FUTEX-GATES-20260804-01/identity.stdout.txt`
- SHA-256: `9c5bcb922536e23f61cbe00a0e0b52ef1c94eb3ffa4755f0a7a11a6aca7d097`
- Test ID: `PHASE5P-FUTEX-GATES-20260804-01`
- Timestamp: `2026-08-03T18:03:30Z` (capture metadata)
- Command: `adb -s G001LT0511550CFT shell id; getenforce; uname -a; getprop ro.build.fingerprint; getprop ro.build.version.incremental`
- Observed result: shell UID 2000; enforcing; AArch64 `4.4.146+`; PS7330 fingerprint.
- Interpretation: device identity and caller context for this sample.
- Confidence: Confirmed
- Related hypothesis: exact Android implementation applicability.

## P5P-DEVICE-002

- Source: device read-only gate capture
- File: `adb/phase5/PHASE5P-FUTEX-GATES-20260804-01/process_status.stdout.txt`
- SHA-256: `4ff983f8743566d0d3d62bf1d76d673404dd52fce89974421a450f992c678695`
- Test ID: `PHASE5P-FUTEX-GATES-20260804-01`
- Timestamp: `2026-08-03T18:03:30Z`
- Command: `adb -s G001LT0511550CFT shell grep ... /proc/self/status`
- Observed result: UID/GID 2000; `CapEff=0`; `Seccomp=0`; bounding set only as captured.
- Interpretation: this sample did not have effective Linux capabilities.
- Confidence: Confirmed
- Related hypothesis: shell reachability.

## P5P-DEVICE-003

- Source: device read-only gate capture
- File: `adb/phase5/PHASE5P-FUTEX-GATES-20260804-01/kernel_sysctls.stdout.txt`
- SHA-256: `c97195478ddb7918a1becf90ed636b31e703319080997cc94450bd826a01883d`
- Test ID: `PHASE5P-FUTEX-GATES-20260804-01`
- Timestamp: `2026-08-03T18:03:30Z`
- Command: read-only `cat` of selected `/proc/sys/kernel/*` paths.
- Observed result: `perf_event_paranoid=3`; other selected sensitive values were denied or absent.
- Interpretation: shell visibility is restricted; it is not a feature enablement result.
- Confidence: Confirmed
- Related hypothesis: whether public offset/diagnostic steps are available to shell.

## P5P-DEVICE-004

- Source: device read-only gate capture
- File: `adb/phase5/PHASE5P-FUTEX-GATES-20260804-01/proc_visibility.stdout.txt`
- SHA-256: `a9feb2a3ad1b566e90cc457e61a5a24e6ecfb72d5be943f6c9c65a6aca45dd1d`
- Test ID: `PHASE5P-FUTEX-GATES-20260804-01`
- Timestamp: `2026-08-03T18:03:30Z`
- Command: read-only `ls -lZ` and `head` for `/proc/kallsyms`, `/proc/kcore`, `/dev/kmem`, `/dev/ion`, `/dev/mtk_cmdq`.
- Observed result: `/proc/kallsyms` denied; `/proc/kcore` and `/dev/kmem` absent; device-node modes and SELinux labels preserved.
- Interpretation: the public aresin symbol-extraction path is not available to this shell context.
- Confidence: Confirmed (visibility scope)
- Related hypothesis: Android port transferability.

## P5P-DEVICE-005

- Source: prior exact runtime config capture
- File: `adb/phase5/PHASE5F-CMDQ-RUNTIME-20260803-02/kernel_config.stdout.txt`
- SHA-256: `9fae0dc507c20842b68f8d0c26b8db8fe7d86c7459acb29cfa5b622e2666cbc9`
- Test ID: `PHASE5F-CMDQ-RUNTIME-20260803-02`
- Timestamp: recorded in the prior Phase 5 runtime capture.
- Command: prior read-only kernel config extraction.
- Observed result: `CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y`, `CONFIG_PREEMPT=y`, `CONFIG_RANDOMIZE_BASE=y`, `CONFIG_PANIC_ON_OOPS=y`, `CONFIG_PANIC_ON_OOPS_VALUE=1`.
- Interpretation: source family is present, but this does not prove an exploitable signed binary.
- Confidence: Confirmed (captured-config scope)
- Related hypothesis: GhostLock applicability.

## P5P-SOURCE-001

- Source: exact Fire source comparison
- File: `artifacts/phase5/exact-futex-sched-review-20260804-04/futex-comparison.json`; `futex-diff.txt`
- SHA-256: see that artifact's `sha256sums.txt`.
- Test ID: `PHASE5O-EXACT-FUTEX-SCHED-20260804-04`
- Timestamp: recorded in the Phase 5O artifact.
- Command: `tools/scripts/analyze_phase5_exact_futex_sched.py` with exact Amazon and stable v4.4.146 inputs.
- Observed result: 27 diff lines / 3 hunks, all visible FPSGO timer hooks; no PI proxy hunk.
- Interpretation: source comparison does not show an Amazon futex PI rewrite.
- Confidence: Confirmed (source scope)
- Related hypothesis: Fire private patch/backport.

## P5P-SOURCE-002

- Source: exact Fire vendor scheduler header comparison
- File: `artifacts/phase5/exact-futex-sched-review-20260804-04/sched-comparison.json`
- SHA-256: see that artifact's `sha256sums.txt`.
- Test ID: `PHASE5O-EXACT-FUTEX-SCHED-20260804-04`
- Timestamp: recorded in the Phase 5O artifact.
- Command: same analysis script with exact vendor `sched.h` and stable v4.4.146 reference.
- Observed result: 966 diff lines / 48 hunks; `task_struct` source line 1685; `pi_blocked_on` line 1945.
- Interpretation: upstream-only task layout calculations are unsafe.
- Confidence: Confirmed (source scope)
- Related hypothesis: exact task offset.

## P5P-ANDROID-001

- Source: pinned public Android implementation
- File: `artifacts/phase5/android-nearby-port-review-20260804-01/repo-metadata.tsv`
- SHA-256: generated in the bundle manifest.
- Test ID: `PHASE5P-ANDROID-NEARBY-PORT-20260804-01`
- Timestamp: 2026-08-04 host review
- Command: GitHub API metadata and pinned raw-document hash commands.
- Observed result: aresin targets MT6893 / Android 13 / Linux 4.14.186; it requires device-specific profiles and documents expected panic/reboot on wrong adaptation.
- Interpretation: nearest public Android implementation is methodology, not a Fire target.
- Confidence: Confirmed (public-source scope)
- Related hypothesis: direct Android portability.

## P5P-ANDROID-002

- Source: pinned Linux headers
- File: `artifacts/phase5/android-nearby-port-review-20260804-01/source-comparison.tsv`
- SHA-256: generated in the bundle manifest.
- Test ID: `PHASE5P-ANDROID-NEARBY-PORT-20260804-01`
- Timestamp: 2026-08-04 host review
- Command: `sed -n '/struct rt_mutex_waiter/,/};/p'` on pinned v4.4.146 and v4.14.186 headers.
- Observed result: common rb_node/task/lock/prio prefix; v4.14 adds `deadline`, changing non-debug size.
- Interpretation: common prefix cannot justify copying the aresin target profile.
- Confidence: Confirmed (header scope)
- Related hypothesis: layout portability.

## P5P-SAFETY-001

- Source: new gate script and output manifests
- File: `tools/scripts/capture_phase5p_futex_gates.sh`; `adb/phase5/PHASE5P-FUTEX-GATES-20260804-01/result.md`
- SHA-256: see output `sha256sums.txt`; script hash is in the Git commit manifest.
- Test ID: `PHASE5P-FUTEX-GATES-20260804-01`
- Timestamp: 2026-08-03T18:03:30Z
- Command: read-only capture only; `--dry-run` was also run.
- Observed result: no futex trigger, no device-node open, no sysctl write, no reboot, no Android state mutation.
- Interpretation: this phase did not attempt root or crash execution.
- Confidence: Confirmed
- Related hypothesis: safe continuation boundary.
