# PHASE6A-PI-SMOKE-T02 result

## Observed result

The exact PS7331 device executed the benign static AArch64 binary once under
the ADB shell domain:

- command: timeout 3s /data/local/tmp/phase6a-pi-lock-smoke-T02
- exit code: 0
- stdout: empty
- stderr: empty
- timeout: false
- binary removed after the run
- ADB remained connected
- build fingerprint remained unchanged

## What this proves

**Confirmed:** a shell-domain process on PS7331 can complete one uncontended
FUTEX_LOCK_PI_PRIVATE followed by FUTEX_UNLOCK_PI_PRIVATE pair.

This strengthens ordinary PI-futex syscall reachability. It does not prove
FUTEX_WAIT_REQUEUE_PI or FUTEX_CMP_REQUEUE_PI reachability, a proxy waiter,
waiter-task/current identity mismatch, cleanup residue, a later consumer,
memory corruption, or privilege transition.

## Safety

The binary did not use requeue-PI operations, multiple threads, a race,
kernel-memory access, credential APIs, boot state, or partition writes. The
only device file was the generated test binary under /data/local/tmp and it
was removed successfully.

Raw evidence:

adb/phase6a/PHASE6A-PI-SMOKE-T02/
