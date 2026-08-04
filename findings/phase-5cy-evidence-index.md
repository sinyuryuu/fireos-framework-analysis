# Phase 5CY evidence index

| Evidence ID | Source | Observation | Interpretation | Confidence |
|---|---|---|---|---|
| P5CY-001 | PS7331 device properties | Exact PS7331 fingerprint, MT8183, Linux 4.4.146+, SELinux enforcing, verified boot green | runtime build identity | Confirmed |
| P5CY-002 | PS7331 kernel config | FUTEX, RT_MUTEXES, TRACEPOINTS, EVENT_TRACING and TRACING enabled | kernel feature/trace infrastructure exists in config | Confirmed, config scope |
| P5CY-003 | PS7331 kernel config | FUNCTION_TRACER, KPROBES, DEBUG_INFO and KALLSYMS_ALL not available in captured config | no direct production function-level observation route from these features | Confirmed, config scope |
| P5CY-004 | device tracing visibility | no `events/futex`; shell cannot read `/proc/kallsyms`; no `/proc/kcore` or `/dev/kmem`; perf paranoid 3 | stock shell lacks a safe waiter/cleanup trace and memory observation surface | Confirmed, visibility scope |
| P5CY-005 | process status | system_server/SystemUI/Microsoft/OTA Seccomp 2; adbd UID 2000, CapEff 0, Seccomp 0 | app/system process policy boundary; adbd is not root | Confirmed |
| P5CY-006 | logcat | bounded all-buffer filter produced zero matching lines | no visible event in this capture; not proof of absence | Unobserved |
| P5CY-007 | HOME pre-snapshot | user_setup_complete=0, device_provisioned=null, OOBE resolver and phase4 alias foreground | test/OOBE state must be excluded from GhostLock conclusions | Confirmed |
| P5CY-008 | foreground-only restore | explicit Fire Launcher start made it resumed/focused; no package/settings change | reversible foreground recovery only | Confirmed |
| P5CY-D1 | runtime | no same-execution waiter identity observation | dynamic identity mismatch remains unobserved | Unobserved |

Raw capture directories and their SHA-256 manifests are listed in
`findings/phase-5cy-ps7331-runtime-observation-boundary.md`.
