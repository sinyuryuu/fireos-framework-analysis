# Phase 5BU evidence index

## P5BU-CONFIG-001

- Source: PS7331 official boot image embedded `IKCONFIG`
- File: `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config`
- SHA-256: `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04`
- Test ID: `P5BU-HOST-CONFIG-01`
- Timestamp: `2026-08-04`
- Command: host-only IKCONFIG extraction already recorded in `metadata.json`; `rg -n 'CONFIG_(FUTEX|RT_MUTEXES|PREEMPT|RANDOMIZE_BASE|ARM64|KALLSYMS|SECCOMP)' kernel.config`
- Observed result: `CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y`, `CONFIG_PREEMPT=y`, `CONFIG_RANDOMIZE_BASE=y`, ARM64 VA39/4K, KALLSYMS and SECCOMP enabled.
- Interpretation: Embedded production-kernel configuration supports the source path.
- Confidence: **Confirmed**
- Related hypothesis: PS7331 has the required kernel subsystems enabled.

## P5BU-SOURCE-001

- Source: PS7331 build-selected `futex.c`
- File: `artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c`
- SHA-256: `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96`
- Test ID: `P5BU-HOST-SOURCE-01`
- Timestamp: `2026-08-04`
- Command: source-only line and token inventory
- Observed result: PI dispatch at lines 3237–3269; proxy call around 1958–1965.
- Interpretation: FUTEX_REQUEUE_PI source path is present.
- Confidence: **Confirmed**
- Related hypothesis: GhostLock source path is reachable in the build-selected tree.

## P5BU-SOURCE-002

- Source: PS7331 build-selected `rtmutex.c`
- File: `artifacts/phase5/ps7331-full-source-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`
- SHA-256: `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde`
- Test ID: `P5BU-HOST-SOURCE-02`
- Timestamp: `2026-08-04`
- Command: `tools/scripts/analyze_phase5bf_ghostlock_reachability.py ...`
- Observed result: `remove_waiter()` current-task cleanup; proxy error path calls `remove_waiter()`.
- Interpretation: The source contains the vulnerable semantic pattern and its proxy caller.
- Confidence: **Confirmed**
- Related hypothesis: PS7331 source is pre-fix.

## P5BU-IMAGE-001

- Source: PS7331 decompressed Image static marker set
- File: `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/symbol-presence.csv` and `instruction-patterns.csv`
- SHA-256: `c82b1881cd62d4519563727968e25bb946615c344de3c3293a013b3cd2788ea0` (symbol presence); `0ee3da7513051f2fa32b221918c6e671bc78b2a8e192fa0ab7ad65cc6e53475d` (instruction patterns)
- Test ID: `P5BU-HOST-IMAGE-01`
- Timestamp: `2026-08-04`
- Command: preserved sanitized Image static review
- Observed result: `futex_requeue`, `rt_mutex_start_proxy_lock`, `remove_waiter` present; current-task cleanup marker and proxy call marker present.
- Interpretation: Inspected Image is consistent with the pre-fix source path.
- Confidence: **Strong evidence**
- Related hypothesis: PS7331 inspected Image did not contain the fixed semantic.

## P5BU-VERIFY-001

- Source: source/config reachability analyzer
- File: `artifacts/phase5/phase5bu-ps7331-embedded-config-reachability-20260804-01/reachability.json`
- SHA-256: `1004d30514f276eb064e19b2baa3aba094564469a14525e14be77ccccb1c1b83`
- Test ID: `P5BU-HOST-VERIFY-01`
- Timestamp: `2026-08-04`
- Command: `python3 -B tools/scripts/analyze_phase5bf_ghostlock_reachability.py` with PS7331 source, embedded config and fixed reference
- Observed result: `SOURCE_AND_CONFIG_REACHABILITY_CANDIDATE`; exact signed binary, runtime exploitability and root all false.
- Interpretation: New evidence strengthens applicability but does not establish a PoC.
- Confidence: **Confirmed**
- Related hypothesis: PS7331 static path is present but live exploit remains unverified.

## P5BU-SAFETY-001

- Source: analyzer output and command manifest
- File: `artifacts/phase5/phase5bu-ps7331-embedded-config-reachability-20260804-01/sha256sums.txt`
- SHA-256: verified by the directory manifest
- Test ID: `P5BU-SAFETY-01`
- Timestamp: `2026-08-04`
- Command: host-only Python and text tools
- Observed result: no ADB, fastboot, bootloader, kernel-memory, unknown-ioctl or partition operation.
- Interpretation: device state unchanged.
- Confidence: **Confirmed**
- Related hypothesis: safety boundary.
