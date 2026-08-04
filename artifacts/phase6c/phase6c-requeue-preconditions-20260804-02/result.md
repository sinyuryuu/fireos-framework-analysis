# Phase 6C requeue-PI precondition model

Host-only source model; no device, syscall, thread, race, memory or payload.

- Single-context/no-waiter: proxy call not reached; identity mismatch not observable.
- Paired-waiter/proxy candidate: proxy call is structurally reachable; this is stateful and outside the stock-device safety boundary.

A single-context no-waiter call can only classify the no-waiter branch; it cannot observe waiter->task versus current. The proxy identity question requires a pre-existing matching waiter and is therefore a stateful runtime experiment, not a harmless switch probe.
