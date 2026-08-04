Phase 5BL host-only analysis of the preserved PS7330 futex gate capture.

The analyzer reads only the raw files under
adb/phase5/PHASE5BL-FUTEX-GATES-20260804-01. It does not invoke adb, open a
device node, trigger futex/PI operations, derive addresses, or write device
state.
