# Phase 6C requeue-PI protocol evidence index

## P6C-PROTO-01

- Source: preserved PS7331 GPL source
- Files: `futextest.h`, `futex_requeue_pi.c`
- Artifact: `artifacts/phase6c/phase6c-requeue-protocol-analysis-20260804-01/protocol-analysis.json`
- Observation: the documented/tested API is split into waiter and waker halves;
  the functional selftest waits for waiter progress before requeue.
- Interpretation: requeue-PI is a stateful paired protocol, not a one-call probe.
- Confidence: **已證實**

## P6C-PROTO-02

- Source: preserved PS7331 GPL source
- File: `futex_requeue_pi_mismatched_ops.c`
- Observation: even the negative mismatch test creates a child waiter, delays,
  issues the requeue operation, then wakes and joins the child.
- Interpretation: an error-path selftest still requires a second execution context.
- Confidence: **已證實**

## P6C-PROTO-03

- Source: `kernel/futex.c`
- Lines: 1716, 1963-1975
- Observation: no-waiter return precedes proxy call and cleanup.
- Interpretation: a no-waiter call cannot observe the proxy identity mismatch.
- Confidence: **高可信推論**

## P6C-RO-01

- Source: selected-serial read-only capture
- File: `adb/phase6c/PHASE6C-RO-CAPTURE-20260804-01/`
- Manifest SHA-256: `c2f8469786d2bb8a1acb8f39eb34ae188dd910f03fdc9e3c98f38171d028a2`
- Observation: PS7331 fingerprint, kernel 4.4.146+, SELinux Enforcing, verified
  boot green, unlocked kernel false.
- Confidence: **已證實（snapshot-scoped）**

## P6C-RO-02

- Source: same capture
- Observation: `/proc/kallsyms` and `randomize_va_space` denied; `/proc/slabinfo`
  absent for shell; no futex or device command was issued.
- Interpretation: shell observability is bounded; this does not prove kernel
  internals or exploitability.
- Confidence: **已證實（shell boundary）**

## P6C-RO-03

- Source: same capture
- Observation: `user_setup_complete=0`; HOME resolver listed OOBE priority 100,
  Fire Launcher priority 50 and sideloaded candidates effective priority 0;
  current foreground was Microsoft Launcher.
- Interpretation: resolver and foreground state differ under this snapshot; the
  setup-state condition must be recorded before any future HOME conclusion.
- Confidence: **已證實（snapshot-scoped）**

## P6C-RO-04

- Source: host-only protocol analyzer
- File: `tools/scripts/analyze_phase6c_requeue_protocol.py`
- Observation: dry-run and real analysis both report no compilation, execution,
  device contact, thread creation, race, memory access or payload generation.
- Confidence: **已證實**
