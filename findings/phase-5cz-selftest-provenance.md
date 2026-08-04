# Phase 5CZ — futex selftest provenance and device presence

Status: **Completed; read-only observation only**

This phase separates three facts that must not be conflated: the PS7331 source
tree contains futex selftests, the kernel build system can build them in a
root-required selftest workflow, and a stock tablet exposes a runnable copy.

## Results

| Question | Result | Classification |
|---|---|---|
| Are futex/requeue-PI selftests present in the PS7331 source index? | Yes, including `futex_requeue_pi.c`, `futex_requeue_pi_mismatched_ops.c`, and `futex_requeue_pi_signal_restart.c`. | **Confirmed** |
| Does the kernel Makefile describe a kselftest build/run path? | Yes; it describes building/running kselftest and says the kernel must be built, installed, booted, and the tests run as root. | **Confirmed** |
| Was a matching selftest binary found in the bounded standard device paths? | No matching lines were observed. | **Confirmed negative observation** |
| Was a selftest copied, built, or executed on the tablet? | No. | **Confirmed** |
| Is the GhostLock runtime identity mismatch established? | No. | **Unobserved / Hypothesis remains** |

## Evidence

The raw read-only capture is retained at:

`adb/phase5/PHASE5CZ-SELFTEST-PRESENCE-20260804-01/`

Its manifest SHA-256 is
`ccf8013148a125e1c2b4299262ba36b321d20b6342f4328f554c1451139a3a66`.
The capture used explicit serial selection and searched only bounded, readable
standard executable/library paths. It did not invoke a futex syscall or any
unknown binary.

The source index identifies the functional tests under the MT8183 4.4 tree.
The kernel Makefile states that kselftest is a root-run workflow and that the
kernel must be built, installed, and booted first. This is not a permission to
run it on the stock device; it is provenance for a future controlled kernel
test environment only.

## Interpretation

The source selftests are useful for understanding the intended public futex
interfaces, but their presence does not prove that Fire userspace can reach
the proxy PI path, that a proxy waiter can produce `waiter->task != current`,
or that any cleanup residue is exploitable. The device-side negative search is
not proof that no equivalent code exists elsewhere, because it was bounded and
did not inspect protected partitions.

No source was built, no test was installed, no futex operation was issued, and
no root, kernel-memory, boot, or partition action was attempted.

Evidence IDs: `P5CZ-E01` through `P5CZ-E05` in
`findings/phase-5cz-evidence-index.md`.
