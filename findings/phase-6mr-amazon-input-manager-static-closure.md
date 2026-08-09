# Phase 6MR — IAmazonInputManager static caller/sink closure

Date: 2026-08-10
Schema: `phase6mr-amazon-input-manager-v1`

## Scope and safety

This is **host-only static analysis** of preserved PS7331 boot-framework and
fosservices disassembly. No ADB, Binder/service call, private transaction,
input injection, device-node access, ioctl, settings/package mutation, reboot,
OTA/recovery, exploit, Root attempt, or partition write was performed.

## Executive result

**已證實：** `IAmazonInputManager.Stub.Proxy` contains 28 virtual methods;
two are inherited Binder helpers (`asBinder` and `getInterfaceDescriptor`) and
the parser maps 26 remote methods to transaction codes 1–26. The service publishes
the matching Binder endpoint as `amazon_input` in
`AmazonInputManagerService.onStart()`.

**已證實：** the corresponding `BinderService` methods are a key/input
control surface. Key-list/listener/interceptor methods perform explicit
`com.amazon.permission.GET_KEYEVENTS` checks. Event-register methods perform
`com.amazon.permission.ACCESS_EVENT_REGISTER` checks. The interceptor method
also contains the bounded system-app, whitelist, and foreground checks recorded
in the method body.

**待驗證：** `inject()` and `injectSequence()` read Binder calling PID/UID and
pass them into `nativeInject`/`nativeInjectSequence`, but their Binder method
windows do not contain a direct permission call. A separate
`checkInjectEventsPermission(II)` helper exists and checks Android and Amazon
inject-event permissions plus a system-UID condition, but no callsite to that
helper was found inside the two bounded Binder method blocks. Native-side
enforcement and any other caller remain **待驗證**; this is not evidence of an
accessible or safe shell route.

**高可信推論（bounded）：** the `AmazonInputManagerService.BinderService`
slice has no `setHomeActivity`, preferred-activity writer, `ACTION_MAIN`,
`CATEGORY_HOME`, or `com.amazon.firelauncher` token. Input callbacks can be
HOME-adjacent only after their authorization/whitelist/foreground conditions;
the slice does not select the HOME component.

**已排除（bounded）：** the presence of `amazon_input`, its proxy, or its
native injection names alone does not establish a shell-accessible HOME
replacement or a Fire Launcher selector.

**因風險拒絕測試：** no `service call amazon_input`, guessed transaction,
`nativeInject*`, device-node, or input event was attempted. Such actions could
alter input routing or foreground control and would not be a necessary test of
the static question.

## Method matrix

| Method | Tx | Permission / gate | Identity | Sink | HOME relevance | Classification |
|---|---:|---|---|---|---|---|
| `createKeyboardDevice` | 7 | none observed in BinderService method block | Binder.getCallingPid; Binder.getCallingUid | nativeCreateKeyboardDevice | not HOME; no resolver/preferred/component writer in method block | Confirmed static method mapping; no direct permission marker in this bounded block |
| `createMouseDevice` | 5 | none observed in BinderService method block | Binder.getCallingPid; Binder.getCallingUid | nativeCreateMouseDevice | not HOME; no resolver/preferred/component writer in method block | Confirmed static method mapping; no direct permission marker in this bounded block |
| `destroyKeyboardDevice` | 8 | none observed in BinderService method block | Binder.getCallingPid; Binder.getCallingUid | nativeDispose | not HOME; no resolver/preferred/component writer in method block | Confirmed static method mapping; no direct permission marker in this bounded block |
| `destroyMouseDevice` | 6 | none observed in BinderService method block | Binder.getCallingPid; Binder.getCallingUid | nativeDispose | not HOME; no resolver/preferred/component writer in method block | Confirmed static method mapping; no direct permission marker in this bounded block |
| `dispatchKeyEventListenerCallbacks` | 20 | none observed in BinderService method block | no caller-identity marker observed | RemoteCallbackList; KeyEventCallback; IKeyEventCallback | indirect key/callback path; no HOME resolver/component writer | Confirmed static method mapping; no direct permission marker in this bounded block |
| `endVolumeAdjustment` | 4 | none observed in BinderService method block | no caller-identity marker observed | return/state-only or sink unresolved in method block | not HOME; volume/audio path | Confirmed static method mapping; no direct permission marker in this bounded block |
| `getLastKeyEventTime` | 21 | none observed in BinderService method block | no caller-identity marker observed | return/state-only or sink unresolved in method block | indirect key/callback path; no HOME resolver/component writer | Confirmed static method mapping; no direct permission marker in this bounded block |
| `getToggleBitRegister` | 23 | com.amazon.permission.ACCESS_EVENT_REGISTER; Missing permission to access event register! | no caller-identity marker observed | return/state-only or sink unresolved in method block | not HOME; no resolver/preferred/component writer in method block | Confirmed: explicit Amazon permission check |
| `inject` | 1 | none observed in BinderService method block; separate checkInjectEventsPermission helper exists; no callsite in bounded method block | Binder.getCallingPid; Binder.getCallingUid | nativeInject | indirect input injection; could carry a key code if authorized, but no HOME resolver/component writer | Strong evidence: Java Binder block has caller pid/uid and native sink; direct permission/native enforcement unresolved |
| `injectSequence` | 2 | none observed in BinderService method block; separate checkInjectEventsPermission helper exists; no callsite in bounded method block | Binder.getCallingPid; Binder.getCallingUid | nativeInjectSequence; nativeInject | indirect input injection; could carry a key code if authorized, but no HOME resolver/component writer | Strong evidence: Java Binder block has caller pid/uid and native sink; direct permission/native enforcement unresolved |
| `postInputEventCallback` | 19 | none observed in BinderService method block | no caller-identity marker observed | return/state-only or sink unresolved in method block | not HOME; no resolver/preferred/component writer in method block | Confirmed static method mapping; no direct permission marker in this bounded block |
| `registerKeyEventIdleTimeListener` | 17 | com.amazon.permission.GET_KEYEVENTS; Requires GET_KEYEVENTS permission | no caller-identity marker observed | RemoteCallbackList; IKeyEventIdleCallback | indirect key/callback path; no HOME resolver/component writer | Confirmed: explicit Amazon permission check |
| `registerKeyEventInterceptor` | 25 | com.amazon.permission.GET_KEYEVENTS; Requires GET_KEYEVENTS permission | Binder.getCallingUid | KeyEventCallback; IKeyEventCallback | indirect key/callback path; no HOME resolver/component writer | Confirmed: explicit Amazon permission check |
| `registerKeyEventListListener` | 13 | com.amazon.permission.GET_KEYEVENTS; Requires GET_KEYEVENTS permission | no caller-identity marker observed | KeyEventCallback; IKeyEventCallback | indirect key/callback path; no HOME resolver/component writer | Confirmed: explicit Amazon permission check |
| `registerKeyEventListener` | 11 | com.amazon.permission.GET_KEYEVENTS; Requires GET_KEYEVENTS permission | no caller-identity marker observed | RemoteCallbackList; KeyEventCallback; IKeyEventCallback | indirect key/callback path; no HOME resolver/component writer | Confirmed: explicit Amazon permission check |
| `registerNextKeyEventListener` | 15 | com.amazon.permission.GET_KEYEVENTS; Requires GET_KEYEVENTS permission | no caller-identity marker observed | RemoteCallbackList; IKeyEventNextCallback | indirect key/callback path; no HOME resolver/component writer | Confirmed: explicit Amazon permission check |
| `setInputFilter` | 9 | none observed in BinderService method block | no caller-identity marker observed | setInputFilter | indirect key/callback path; no HOME resolver/component writer | Confirmed static method mapping; no direct permission marker in this bounded block |
| `setLedState` | 10 | none observed in BinderService method block | no caller-identity marker observed | return/state-only or sink unresolved in method block | not HOME; no resolver/preferred/component writer in method block | Confirmed static method mapping; no direct permission marker in this bounded block |
| `setToggleBitButtonMap` | 24 | com.amazon.permission.ACCESS_EVENT_REGISTER; Missing permission to access event register! | no caller-identity marker observed | return/state-only or sink unresolved in method block | not HOME; no resolver/preferred/component writer in method block | Confirmed: explicit Amazon permission check |
| `setToggleBitRegister` | 22 | com.amazon.permission.ACCESS_EVENT_REGISTER; Missing permission to access event register! | no caller-identity marker observed | return/state-only or sink unresolved in method block | not HOME; no resolver/preferred/component writer in method block | Confirmed: explicit Amazon permission check |
| `startVolumeAdjustment` | 3 | none observed in BinderService method block | no caller-identity marker observed | return/state-only or sink unresolved in method block | not HOME; volume/audio path | Confirmed static method mapping; no direct permission marker in this bounded block |
| `unRegisterKeyEventIdleTimeListener` | 18 | com.amazon.permission.GET_KEYEVENTS; Requires GET_KEYEVENTS permission | no caller-identity marker observed | RemoteCallbackList; IKeyEventIdleCallback | indirect key/callback path; no HOME resolver/component writer | Confirmed: explicit Amazon permission check |
| `unRegisterKeyEventInterceptor` | 26 | com.amazon.permission.GET_KEYEVENTS; Requires GET_KEYEVENTS permission | no caller-identity marker observed | KeyEventCallback; IKeyEventCallback | indirect key/callback path; no HOME resolver/component writer | Confirmed: explicit Amazon permission check |
| `unRegisterKeyEventListListener` | 14 | com.amazon.permission.GET_KEYEVENTS; Requires GET_KEYEVENTS permission | no caller-identity marker observed | KeyEventCallback; IKeyEventCallback | indirect key/callback path; no HOME resolver/component writer | Confirmed: explicit Amazon permission check |
| `unRegisterKeyEventListener` | 12 | com.amazon.permission.GET_KEYEVENTS; Requires GET_KEYEVENTS permission | no caller-identity marker observed | RemoteCallbackList; KeyEventCallback; IKeyEventCallback | indirect key/callback path; no HOME resolver/component writer | Confirmed: explicit Amazon permission check |
| `unRegisterNextKeyEventListener` | 16 | com.amazon.permission.GET_KEYEVENTS; Requires GET_KEYEVENTS permission | no caller-identity marker observed | RemoteCallbackList; IKeyEventNextCallback | indirect key/callback path; no HOME resolver/component writer | Confirmed: explicit Amazon permission check |

The complete machine-readable matrix is
`artifacts/phase6mr-amazon-input-manager-20260810-01/method-matrix.csv`.

## Exact source anchors

| Evidence | File / lines | Meaning | Classification |
|---|---|---|---|
| 6MR-E01 | `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:388887-389899` | Proxy class, 28 virtual methods, transaction code constants | Confirmed static |
| 6MR-E02 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:19198-20547` | BinderService implementations | Confirmed static |
| 6MR-E03 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:21718-21776` | Android/Amazon inject permission helper and UID condition | Confirmed static |
| 6MR-E04 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:21775-21794` | generic `checkCallingOrSelfPermission` → SecurityException helper | Confirmed static |
| 6MR-E05 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:22640-22656` | `amazon_input` Binder publication | Confirmed static |
| 6MR-E06 | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:19198-20547` | bounded absence of HOME/preferred/Fire component tokens | Strong evidence (bounded) |

## Decision points relevant to HOME

```text
IAmazonInputManager.Proxy
  → IBinder.transact(code)
  → ServiceManager endpoint "amazon_input"
  → BinderService method
  → permission / identity / whitelist checks where present
  → input callback or native input sink
  → [no HOME resolver or preferred-activity writer in this slice]
```

`registerKeyEventInterceptor` is the closest input-side HOME boundary: the
method checks `GET_KEYEVENTS`, resolves the caller/package context, requires a
system-app condition, checks whitelist entries, and requires the caller's
foreground package in the preserved code. This can explain why privileged
Amazon components may observe or consume a key, but it does not prove a direct
Fire Launcher launch.

`inject` and `injectSequence` are distinct: they route event data to native
input devices. Their Java blocks carry Binder caller identity into the native
call, while the separate permission helper is not called in those blocks. The
native implementation, SELinux device access, service-handle availability, and
runtime behavior remain unobserved. Do not infer an exploit, input bypass, or
HOME replacement from this static gap.

## Scope limits and next minimal target

The matrix closes this interface's proxy→transaction→BinderService mapping and
records its bounded authorization/sink shape. It does not prove which clients
obtain the service handle at runtime, which UID owns the service process, or
what the native implementation enforces. The next safe target, if research
continues, is host-only mapping of the remaining unindexed Amazon service
interfaces; no private transaction replay is justified by this result.

## Input hashes

```text
{
  "artifacts/phase6aj/input-home-boundary-20260805-05/input-home-boundary.csv": "1d56fd986194345f45f019b8e4d578476f10ddd745bc9dbbb8a48c6fc7174379",
  "decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log": "fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71",
  "decompiled/baksmali/vdexExtractor/fosservices/disassembly.log": "ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c",
  "findings/phase-6aj-input-home-boundary.md": "98dcbc10f11782bf4268f1cc5bf43cbea3711f012495b43a8128642864dd989c",
  "findings/phase-6mn-ipc-user-scope-closure.md": "2adc3dd733dbc310da2706a14e9e7f12759198c09f37a63970f35c97855f383e",
  "work/luna_worker_phase6mp_inventory_20260810.md": "16eb678a5d79fb5dd8344ea41a95028e1c9dda4717e92b3c68a01396ac44757e"
}
```

## Reproduction

```sh
python3 tools/scripts/audit_phase6mr_amazon_input_manager.py --dry-run
python3 tools/scripts/audit_phase6mr_amazon_input_manager.py
```

Generated artifact: `artifacts/phase6mr-amazon-input-manager-20260810-01`.
