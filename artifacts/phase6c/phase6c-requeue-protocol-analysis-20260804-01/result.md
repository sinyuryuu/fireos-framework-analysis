# Phase 6C requeue-PI protocol analysis

Host-only source analysis. No compilation, execution, device contact, thread creation, race scheduling, kernel memory access or payload.

The preserved PS7331 selftests define requeue-PI as a paired, stateful protocol. A single-thread/single-call probe can classify only the no-waiter or argument-validation boundary; it cannot validate the proxy identity condition or cleanup consequence.

The protocol matrix records why the proxy identity question is not covered by a single-call switch probe.
