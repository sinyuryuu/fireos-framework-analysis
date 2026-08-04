# Phase 5CQ evidence index

本輪為 host-only reference/source audit。沒有裝置操作、kernel execution、futex syscall、race trigger、kernel memory access 或 payload。

| Evidence ID | Source | Location | Observation | Classification |
|---|---|---|---|---|
| `P5CQ-001` | AOSP Android 9 r61 bionic | `libc/bionic/pthread_cond.cpp`, signal/broadcast path | condition-variable signal/broadcast uses bionic futex wake helper | Confirmed, AOSP reference scope |
| `P5CQ-002` | AOSP Android 9 r61 bionic | `libc/bionic/pthread_cond.cpp`, wait path | condition-variable wait uses bionic futex wait helper | Confirmed, AOSP reference scope |
| `P5CQ-003` | AOSP bionic UAPI | `libc/kernel/uapi/linux/futex.h` | PI and requeue-PI operation constants are exposed to native userspace | Confirmed, UAPI reference scope |
| `P5CQ-004` | AOSP Android 9 r61 bionic | `libc/SYSCALLS.TXT` | no dedicated futex generated syscall-stub entry observed | Confirmed negative observation, reference scope |
| `P5CQ-005` | AOSP Android 9 r61 bionic | app seccomp whitelist/blacklist reference files | policy files describe AOSP reference generation boundary | Confirmed, reference scope |
| `P5CQ-006` | PS7331 Phase 5CO/5CP artifacts | `findings/phase-5co-*`, `findings/phase-5cp-*` | kernel source/config and proxy dataflow exist; this does not prove userspace caller | Confirmed, source/config scope |
| `P5CQ-007` | PS7331 Phase 5CK/5CM captures | `adb/phase5/PS7331-*` | shell visibility/tracing boundary captured; Fire app-domain futex policy not measured | Confirmed limitation |
| `P5CQ-008` | Phase 5CP generated artifact | `artifacts/phase5/phase5cp-proxy-context-20260804-01/proxy-context.json` | source-only classification; runtime mismatch/cleanup not observed | Confirmed, host audit scope |
| `P5CQ-009` | repository search | `artifacts/phase5`, `decompiled` | no Fire-specific native requeue-PI caller was established by this bounded search | Negative observation only; not absence proof |
| `P5CQ-SAFETY-001` | Phase 5CQ process | report/script scope | no syscall, trigger, payload, address, device I/O or privilege operation | Confirmed safety scope |

## Interpretation rule

`P5CQ-001`–`P5CQ-005` describe AOSP/reference userspace, not the installed Fire OS binary. `P5CQ-006`–`P5CQ-008` describe the existing PS7331 source/config/runtime evidence. `P5CQ-009` is deliberately a bounded negative observation and must not be promoted to proof that no native caller exists.
