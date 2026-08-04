Phase 5BJ host-only GhostLock fix-marker comparison

Inputs:
- PS7330 source-family rtmutex.c extracted from the official 7.3.3.0 source review.
- PS7331 build-selected MT8183 rtmutex.c extracted from the official 7.3.3.1 source.
- A pinned fixed-reference rtmutex.c containing waiter::task cleanup.

The checker only searches the remove_waiter() function body and records source
hashes and semantic markers. It does not execute kernel code, calculate runtime
addresses or offsets, build an exploit, contact the device, or write any device
state.

Result: both PS7330 source family and PS7331 build-selected source classify as
PRE_FIX_CURRENT_TASK_CLEANUP; the fixed reference classifies as
FIXED_WAITER_TASK_CLEANUP.
