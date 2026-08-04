# Phase 5CR evidence index

本輪使用 PS7331 實機只讀 pull 與主機端 ELF analysis。沒有執行裝置 native
binary、futex、race、ioctl、kernel memory access 或 root payload。

| Evidence ID | Source | Location/Hash | Observation | Confidence |
|---|---|---|---|---|
| `P5CR-001` | PS7331 Fire libc | `/system/lib64/libc.so`, SHA-256 `0899e7cde39ccae24a3ba7e9f5433922a30f03ed93744af87e053639ce076681` | ELF AArch64, not stripped, contains bionic source labels | Confirmed, artifact scope |
| `P5CR-002` | PS7331 Fire libc | `_Z15__futex_wait_exPVvbibPK8timespec`, text `0x22048` | generic futex wait helper exists and calls libc syscall boundary | Confirmed, disassembly scope |
| `P5CR-003` | PS7331 Fire libc | `_Z18__futex_pi_lock_exPVvbbPK8timespec`, text `0x22128` | PI-lock helper exists and calls libc syscall boundary | Confirmed, disassembly scope |
| `P5CR-004` | PS7331 Fire libc | `pthread_cond_wait 0x82798`, timed variants `0x82800/0x828b0` | condition-variable paths call generic wait helper | Confirmed, call-site scope |
| `P5CR-005` | PS7331 Fire libc | `PIMutexTimedLock 0x83ed0`, `pthread_mutex_lock 0x83dd8` | PI mutex path calls PI-lock helper | Confirmed, call-site scope |
| `P5CR-006` | PS7331 Fire libc bounded search | `strings`, `nm`, `objdump` outputs in local capture/analysis | no requeue-PI caller established in this libc | Negative observation only |
| `P5CR-007` | PS7331 native capture | `linker64` SHA `124745b0...e6ee21b`, `app_process64` SHA `c075e6...67ec01e` | companion artifacts preserved for provenance; no futex conclusion from them | Confirmed, artifact scope |
| `P5CR-008` | PS7331 device | fingerprint `PS7331.4463N/0031575863172`, shell UID 2000 | explicit serial, ADB state `device`, read-only pull | Confirmed, capture scope |
| `P5CR-009` | host analyzer | `artifacts/phase5/phase5cr-fire-libc-analysis-20260804-01/analysis.json` | generic wait edge and PI-lock helper edge true; requeue-PI caller false | Confirmed, bounded call-edge scope |
| `P5CR-RUNTIME-001` | existing Phase 5CP captures | no same-execution proxy trace | identity mismatch not observed | Runtime unobserved |
| `P5CR-SAFETY-001` | Phase 5CR process | capture script/report scope | device not mutated; no native execution/syscall/race/payload | Confirmed safety scope |

## Raw capture

`artifacts/phase5/phase5cr-fire-native-20260804-02/`
