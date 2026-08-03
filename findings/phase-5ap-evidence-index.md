# Phase 5AP evidence index

| Evidence ID | Source | File | Observation | Confidence |
|---|---|---|---|---|
| `P5AP-001` | Device identity | `adb/phase5/PHASE5AP-KERNEL-SYMBOL-20260804-01/identity.stdout.txt` | PS7330 fingerprint, KFTRWI/trona, Linux 4.4.146+, shell UID 2000 | 已證實 |
| `P5AP-002` | Procfs policy | `adb/phase5/PHASE5AP-KERNEL-SYMBOL-20260804-01/symbol_policy.stdout.txt` | `/proc/kallsyms` and `kptr_restrict` denied; `perf_event_paranoid=3` | 已證實 |
| `P5AP-003` | Kallsyms attempt | `adb/phase5/PHASE5AP-KERNEL-SYMBOL-20260804-01/kallsyms.stderr.txt`, `adb/phase5/PHASE5AP-KERNEL-SYMBOL-20260804-01/relevant_symbols.stderr.txt` | shell cannot read or grep `/proc/kallsyms` | 已證實 |
| `P5AP-004` | Read-only kernel surface | `adb/phase5/PHASE5AP-KERNEL-SYMBOL-20260804-01/proc_version.stdout.txt`, `adb/phase5/PHASE5AP-KERNEL-SYMBOL-20260804-01/modules.stdout.txt` | version/modules readable; no state mutation | 已證實 |
| `P5AP-005` | Risk boundary | `findings/phase-5ap-kernel-symbol-surface.md` | no procfs bypass, race, ioctl, root stage or boot operation | 因風險拒絕測試 |
