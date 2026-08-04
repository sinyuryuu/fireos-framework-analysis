# Phase 5BF evidence index

| Evidence ID | Source | File | SHA-256 | Observation | Confidence |
|---|---|---|---|---|---|
| `P5BF-SOURCE-001` | Official PS7331 source bundle, build-selected path | `artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | `remove_waiter()` lines 1079–1129 clears `current->pi_blocked_on`; proxy error line 1684 calls it | Confirmed, source scope |
| `P5BF-SOURCE-002` | Official PS7331 source bundle, build-selected path | `artifacts/phase5/exact-kernel-source-review-7331-nested-platform-members-20260804-01/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c` | `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96` | PI requeue operations, `futex_requeue()` and proxy-lock call site are present | Confirmed, source scope |
| `P5BF-CONFIG-001` | Captured device kernel config | `adb/phase5/PHASE5AQ-DEVICE-CONFIG-20260804-02/kernel.config` | `9fae0dc507c20842b68f8d0c26b8db8fe7d86c7459acb29cfa5b622e2666cbc9` | `CONFIG_FUTEX=y`, `CONFIG_RT_MUTEXES=y`, plus ARM64/preemption focus values | Confirmed, captured-config scope |
| `P5BF-FIX-001` | Public fixed reference source | `artifacts/phase5/public-source-review/linux-rtmutex/linux-stable-v6.1.175.c` | `c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a` | Fixed reference uses `waiter->task` cleanup in `remove_waiter()` | Confirmed, reference scope |
| `P5BF-BINARY-001` | Earlier PS7331 signed Image inspection | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/summary.json` | `eede2b264a6a3a9934cc09b374ae9162e4196d2bdf68a07d6cd5fe2156148f2b2` | Inspected function pattern reads current-task source and proxy path calls `remove_waiter` | Confirmed, inspected-function scope |
| `P5BF-DEVICE-001` | Read-only device postcheck | `adb/phase5/PHASE5BD-DEVICE-POSTCHECK-20260804-01/` | Per-file hashes in `sha256sums.txt` | Device remains PS7330, ADB `device`, resolver is Fire Launcher | Confirmed, snapshot scope |
| `P5BF-OTA-001` | PS7331 OTA metadata and updater inspection | `artifacts/phase5/ps7331-ota-metadata-inspection-20260804-01/` | `54c59cfc445e1b7ff7d6be7dc21b02668260e24b66dbcd53c3c2cf256928395a` (summary) | Full-block OTA metadata; no member installed or written | Confirmed, metadata scope |
| `P5BF-MODEL-001` | Deterministic host-only analyzer | `artifacts/phase5/ghostlock-reachability-review-20260804-04/reachability.json` | `71de526dc9aebe11d1a40b1f6cba664b2abb5be6e7ae21b27b666f10c1421d1e` | Candidate classification; device I/O, execution, payload and addresses explicitly false | Confirmed, analysis scope |
| `P5BF-CVE-001` | Public CVE description and upstream patch reference | [NVD CVE-2026-43499](https://nvd.nist.gov/vuln/detail/CVE-2026-43499) | N/A, web source | Public description matches the source-level waiter/current cleanup distinction | Strong evidence |

## Boundary

These records establish source/config compatibility evidence only. They do not
establish exact PS7330 signed-image equivalence, runtime exploitability, or a
privilege transition.
