# Phase 6B／6C follow-up status

## Current result

Phase 6A confirms only ordinary uncontended PI lock/unlock from an untrusted app.
Phase 6B confirms the source/config layout model and shows that the requeue-PI
`rt_mutex_waiter` is stack-resident in the inspected path. Phase 6C now adds a
host-only instruction-level audit of the PS7331 `/init` policy-loader surface.

## What changed in the evidence chain

**已證實：** the PS7331 image contains code-level references to both standard and
`rootable_*` SELinux policy paths, with two call sites into a common stripped helper
using different flag values. A separate function compares
`androidboot.selinux`/`permissive`.

**高可信推論：** the alternate policy files are connected to a real loader/config
surface, not merely unused strings.

**待驗證：** which policy is active on the current boot, and whether any policy
selection can be changed without boot/system mutation.

**已排除：** these static markers do not prove rootability, a GhostLock runtime
mismatch, cleanup residue, memory corruption, or privilege escalation.

## Next safe research boundary

1. Expand host-only provenance: compare the exact PS7331 source build/config,
   image policy files, and `/init` references; keep all outputs offline.
2. If a lab is later prepared, keep it isolated and instrumented; do not copy an
   instrumented image or test binary to the stock tablet.
3. Treat any paired requeue-PI, race, panic, heap shaping, kernel memory, policy
   mutation, or root experiment as outside the current no-loss boundary and as a
   separate approval item, not as a harmless syscall probe.

The current evidence is sufficient to improve provenance, but not to claim a live
GhostLock trigger or temporary root.
