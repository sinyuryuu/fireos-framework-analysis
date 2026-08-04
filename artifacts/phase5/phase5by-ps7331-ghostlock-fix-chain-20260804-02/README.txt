Phase 5BY host-only GhostLock primary/follow-up fix-chain audit.

The selected PS7331 rtmutex.c is inspected for the pre-fix current-task
cleanup, early deadlock return before waiter assignment, and proxy cleanup
call. The checker does not compile or execute kernel code, access a device,
trigger futexes, calculate offsets, or generate a payload.
