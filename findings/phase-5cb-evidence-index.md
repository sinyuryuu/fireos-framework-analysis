# Phase 5CB evidence index

日期：2026-08-04；scope：PS7331 only；host-only。

| Evidence ID | Source | File | SHA-256 | Observation | Confidence |
|---|---|---|---|---|---|
| P5CB-001 | Exact PS7331 futex source | `artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/futex.c` | `ca9140bac21e62154462315abc9f047f5f69dff4a12d8a03d88986ba54ca7a96` | syscall → `do_futex` → PI requeue → proxy call | Confirmed |
| P5CB-002 | Exact PS7331 rtmutex source | `artifacts/phase5/ps7331-full-source-members-20260804-02/extracted/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c` | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` | proxy API and cleanup relationship | Confirmed |
| P5CB-003 | Embedded IKCONFIG | `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config` | `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04` | FUTEX/RT_MUTEXES/SECCOMP/SELINUX enabled | Confirmed |
| P5CB-004 | Host-only analyzer | `artifacts/phase5/phase5cb-ps7331-futex-entry-audit-20260804-01/entry-audit.json` | generated manifest | source path present; policy unresolved | Confirmed |
| P5CB-005 | Scoped search | analyzer `direct_credential_gate.matches` | generated result | no direct capability/security hook in scoped functions | Confirmed, scoped |
| P5CB-006 | Safety record | `findings/phase-5cb-ps7331-futex-entry-audit.md` | repository commit hash | no syscall/PoC/device execution | Confirmed |
