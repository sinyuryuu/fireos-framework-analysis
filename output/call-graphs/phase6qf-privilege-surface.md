# Phase 6QF privilege-surface graph (text form)

The graph is intentionally a reachability graph rather than an exploit recipe:

```text
source or published capability
  -> exact image / service registration
  -> SELinux label, init mode, or Binder contract
  -> caller identity and permission gate
      -> ordinary app/shell: observed denial or unresolved provenance
      -> accepted trusted caller: user/profile/role propagation
  -> sensitive sink
      -> PackageManager / HOME / package state
      -> OTA / recovery / credential / SELinux / partition
  -> impact only if the complete caller-to-sink chain is closed
```

The three Phase 6QF inputs map into this graph as follows:

| input | mapped edge | result |
|---|---|---|
| Amazon IPC provenance | service registration → Stub/facade → caller/gate → user → sink | Several service and sink edges are confirmed; low-privilege caller closure is not. |
| Exact-image policy/client | source → init/node/file context → SELinux/domain → client → sink | Source and policy markers exist; exact shipped client/allow/reachability remain `UNKNOWN` on several surfaces. |
| Existing runtime audit | read-only state and prior mutation result | Confirms selected denials and current HOME state; it does not create a new writer. |

Dashed/unknown edges are evidence gaps, not implied permission. Risk-rejected
edges were not traversed: unknown Binder transactions, private broadcasts,
device-node open/ioctl, OTA/recovery, Root, remount, SELinux mutation and
partition writes.
