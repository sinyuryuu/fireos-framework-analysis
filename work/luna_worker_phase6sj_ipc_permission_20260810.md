# Phase 6SJ — IPC permission closure

Date: 2026-08-10. Host-only review of the current worktree. No adb, `service call`, Binder transaction, device mutation, or edits outside this report and its CSV companion were performed.

## Result

The exact-build permission declaration for `amazon.permission.ADD_RM_PKG_METADATA` is confirmed at XML lines 1936–1938, with raw `protectionLevel=0x80000002` (`signature|privileged`). The four Amazon Package Manager Binder methods—remove/set flags and remove/set metadata—each perform a method-local `checkCallingOrSelfPermission` and then delegate to `AmazonApplicationFlags`; their persistence sink is metadata/flags `writeToFile`, not a preferred-HOME or application/component-enabled-state setter.

The permission holder/grant and real production caller remain `UNKNOWN`. The bounded privapp/platform-privapp/sysconfig/holder corpus has no exact custom-permission holder row, but that is not proof of global absence. The proxy, Binder contract, service publication, and method implementation establish a private API edge, not a package, UID, signing certificate, or runtime caller.

`AmazonProfileService` is a separate private service. Its bounded check uses `com.amazon.device.permission.PROFILE_INTERACTION` with process ID and user ID, while publication exposes `amazonprofileservice`; the holder remains unknown. Generic `onTransact` and `getCallingUid` occurrences were not attributable to the ADD_RM methods, so caller-identity closure is preserved as `UNKNOWN`.

The only exact Amazon enabled-state edge found in this review is the KFT child/profile path: `enableKftLauncherComponent(UserInfo)` uses the supplied `UserInfo.id` to enable Tahoe and set Fire/Launcher3 application states. That closes child/profile scope, not a User-0 preferred-HOME selector. The ADD_RM metadata path has no bounded static edge to `setHomeActivity`, preferred-activity replacement, or enabled-state mutation; this is `BOUNDED_NOT_FOUND`, not a universal negative.

## Reconciliation with Phase 6SF

This report does not repeat Phase 6SF's permission declaration analysis. It carries forward its correction that the declaration exists, while narrowing the IPC question to service publication, method gates, identity handling, holder/grant status, caller provenance, and state sinks. Phase 6SF's `UNKNOWN` conclusions for holder/grant, requested/granted package join, and actual production caller remain unchanged.

## Evidence index

The CSV contains 10 evidence rows. Every row includes an existing source path, SHA-256, line/range, confidence, and an explicit status. The most material ranges are:

- `fosservices/disassembly.log:95955-96026`: all four `ADD_RM_PKG_METADATA` checks and delegate calls.
- `fosservices/disassembly.log:96132-96136`: Amazon Package Manager BinderService publication.
- `fosservices/disassembly.log:54310-54324`: child/profile-scoped enabled-state writer.
- `018_android.amazon.perm.xmltree.txt:1936-1938`: exact permission declaration.
- `sink-calls.csv:126-130`: separate preferred-HOME/enabled-state sink definitions and gates.

No finding authorizes a private transaction or implies an ordinary-app relay. Caller, holder, and grant fields remain unknown wherever the corpus does not close them.
