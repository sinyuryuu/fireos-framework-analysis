# Phase 6NI — OOBE sender system-context user-scope closure

This is a host-only verification of preserved PS7331 VDEX and `fosinit`
artifacts. No device, Binder, OTA, updater, or package/settings mutation was
performed.

## Verified chain

```text
SystemServer.createSystemContext()
  -> ActivityThread.systemMain()
  -> ActivityThread.getSystemContext()
  -> ContextImpl.createSystemContext()
  -> ContextImpl constructor with null UserHandle
  -> Process.myUserHandle() default
  -> AmazonPackageManagerService.mContext
  -> onBootPhase(550) + isUpgrade()
  -> mContext.sendBroadcast(BOOT_AFTER_SYSTEM_OTA, permission)
  -> framework broadcast user derived from ContextImpl.getUserId()
```

The preserved code therefore supports **Strong evidence** that the sender is a
system-server context path whose user is the system process user by default.
The selected fragments do not encode a child `UserInfo`, a `USER_ALL` target,
or a HOME/preferred-activity setter. The exact numeric runtime user remains a
runtime/build-context fact and is not promoted here to an unconditional User 0
claim.

## Boundary

The receiver's already-closed OOBE path uses its delivered context for
component/settings operations. It does not, in the reviewed source, call
`setHomeActivity`, `replacePreferredActivity`, or a formal HOME role setter.
Consequently this chain is lifecycle/setup evidence, not a launcher replacement
or a shell-callable privilege relay.

## Confidence labels

- **已證實：** system-server creates and owns the sender context path; the
  context default derives from the process user; the OTA broadcast is guarded
  and permission-protected.
- **高可信推論：** on this Android system-server path the effective user is the
  system user, conventionally user 0, but this report does not replace a live
  numeric observation.
- **待驗證：** exact runtime numeric delivery user on this particular build;
  complete runtime `fosinit` loading outside the preserved corpus.
- **已排除（bounded）：** the reviewed OOBE helper is a direct formal HOME
  preference writer.
- **因風險拒絕測試：** manual protected-broadcast replay, OTA/recovery
  execution, package/state mutation, and partition writes.
