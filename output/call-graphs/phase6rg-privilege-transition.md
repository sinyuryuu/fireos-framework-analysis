# Phase 6RG privilege-transition graph (text form)

```text
official PS7331 source / image / package
  -> registration or shipped config
  -> Binder Stub, init, file_context, CIL, manifest
  -> caller / permission / SELinux gate
      -> ordinary app/shell: no accepted high-impact path observed
      -> trusted system/owner/profile/OTA lifecycle: identity and user propagation
  -> sensitive sink
      -> PackageManager / HOME / package state
      -> Settings / DPM / profile state
      -> OTA / recovery / partition capability
      -> driver / procfs / native client
```

Existing runtime captures attach to the graph as observations, not new writers.
Accessibility/foreground redirection terminates at a delayed explicit launch and
does not enter the formal HOME resolver or a privileged identity transition.
`UNKNOWN` caller/client/permission-holder/consumer edges remain unclosed. The
following edges were intentionally not traversed: unknown Binder transactions,
private broadcasts, device-node open/ioctl, OTA/recovery replay, Root/exploit,
remount, SELinux mutation and partition write.
