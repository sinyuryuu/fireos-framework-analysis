# Phase 6B host-only requeue-PI selftest role analysis

This artifact inventories source/build inputs only. No selftest was
compiled, executed, installed, or sent to a device.

## Findings

- `futex_requeue_pi.c` contains waiter, broadcast-waker, signal-waker and
  optional third-party blocker roles; it uses pthread creation/join and
  both WAIT_REQUEUE_PI and CMP_REQUEUE_PI operations.
- `futex_requeue_pi_mismatched_ops.c` creates a blocking child before the
  CMP_REQUEUE_PI call, then joins and wakes it.
- `futex_requeue_pi_signal_restart.c` creates a real-time waiter, uses
  signals and joins it around the requeue operation.
- The functional Makefile links with `-pthread`; the run script executes
  multiple requeue-PI scenarios, not a single switch check.

## Evidence labels

- **已證實：** preserved PS7331 source contains the listed roles and API markers.
- **高可信推論：** a single-thread, single-call harness cannot reproduce the
  selftest's proxy-waiter setup or serve as equivalent GhostLock runtime evidence.
- **待驗證：** whether any shipped Fire userspace component creates the same
  role pairing at runtime.
- **因風險拒絕測試：** building/running these tests on the stock tablet or
  adapting them into a race/root trigger.

## Input hashes

- `futex_requeue_pi`: `1ed88169b15385b97643e7621f1582b605eccacef7bba3de90142fc9e6a45cc2`
- `futex_requeue_pi_mismatched_ops`: `0862834b8cdfa12f93bf71b8b83b1c8f8dcfb9ae995ff8afc58a30b86047461d`
- `futex_requeue_pi_signal_restart`: `d4a5e6926ca10568d11b6f46003dd3817824496de5d337ecd425dc6d7662a2cd`
- `functional_Makefile`: `1a202de8cdd825fa43ebb8e6981a0241385ca93ddb70afeddc6781750222cc3e`
- `functional_run_sh`: `344653a8e618e00fd1a33fcc1f5c5f92688c5f84ff36e6c4adddecd7d85caa30`
- `futex_Makefile`: `166b2f606a97422c6654402c5f89c12ae2aaddea8b8190f62fda22fcb75e86d5`
