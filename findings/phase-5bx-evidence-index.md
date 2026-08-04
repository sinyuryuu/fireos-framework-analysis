# Phase 5BX evidence index

| Evidence ID | Source | File / location | SHA-256 | Observation | Classification |
|---|---|---|---|---|---|
| P5BX-001 | PS7331 build-selected `futex.c` | `.../futex.c:1959-1965,3237-3269` | `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96` | PI requeue dispatch and `rt_mutex_start_proxy_lock(..., this->task)` present | Confirmed, source scope |
| P5BX-002 | PS7331 build-selected `rtmutex.c` | `.../rtmutex.c:1089,1125-1126,1656-1691` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | Proxy error calls `remove_waiter`; cleanup uses current task | Confirmed, pre-fix source scope |
| P5BX-003 | PS7331 embedded config | `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config:169,248,363` | `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04` | FUTEX, RT_MUTEXES and PREEMPT enabled | Confirmed, config scope |
| P5BX-004 | Fixed reference | `linux-stable-v6.1.175.c:remove_waiter()` | `c307ed54156d1f16e82387df7b214445dddf27be8a880f31575f698ca07d880a` | Fixed semantics use `waiter->task` | Confirmed, reference scope |
| P5BX-005 | Reproducible host analyzer | `artifacts/phase5/phase5bx-ps7331-exact-path-audit-20260804-01/reachability.json` | `47fefb040398f81e240fc24b626f80aec765310e6d9b034cd188207d52ebf0a5` | `SOURCE_AND_CONFIG_REACHABILITY_CANDIDATE`; no runtime/root proof | Confirmed, host-only |
| P5BX-006 | KoCleo public metadata | `artifacts/phase5/mtk-easy-su-current-review-20260804-01/repo-metadata.tsv` | `909ed48dbf2442d53ff140d46148a25ce1fda63cedce5dac9ac36e512997e13d` | Pinned mtk-su64 equals previously executed payload | Confirmed, public/source scope |
| P5BX-007 | Prior exact-device test | `findings/phase-5e-mtk-su-t03-result.md` | `ea357d577684fa6f487f52ea23e218b4e65af4ea790c456b1db2fe1df646cd8d` | Exit 1, `Failed critical init step 3`, no UID 0 | Confirmed, tested-payload scope |
| P5BX-008 | PS7331 Image review | `artifacts/phase5/ps7331-rtmutex-static-review-20260804-01/` | `c82b1881cd62d4519563727968e25bb946615c344de3c3293a013b3cd2788ea0` | Current-task cleanup and proxy markers present | Strong evidence, inspected Image scope |

No evidence in this index authorizes live exploit execution or boot-chain writes.
