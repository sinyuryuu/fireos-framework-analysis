# Phase 6MR evidence index — IAmazonInputManager static closure

Generated: 2026-08-10
Test ID: `PHASE6MR-STATIC-20260810-01`
Scope: host-only; no device/Binder/input/ioctl/mutation/reboot.

## 6MR-E01 — proxy and transaction map

- Source: `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log:388887-389899`
- SHA-256: `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`
- Command: `python3 tools/scripts/audit_phase6mr_amazon_input_manager.py`
- Observed: 28 virtual methods including `asBinder` and `getInterfaceDescriptor`; 26 remote methods carry codes 1–26.
- Interpretation: proxy/transaction shape is statically reproducible.
- Confidence: Confirmed static
- Related hypothesis: the interface is a HOME resolver writer — not shown.

## 6MR-E02 — BinderService implementation map

- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:19198-20547`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Command: same host-only audit
- Observed: all 26 proxy remote method names have matching `AmazonInputManagerService.BinderService` method blocks.
- Interpretation: interface-to-implementation mapping is name/descriptor aligned in the preserved disassembly.
- Confidence: Confirmed static
- Related hypothesis: proxy existence proves caller reachability — Disproved.

## 6MR-E03 — injection permission helper

- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:21718-21776`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Observed: helper reads Binder calling PID/UID, checks `android.permission.INJECT_EVENTS` and `com.amazon.permission.INJECT_EVENTS`, and allows system UID condition on the shown branch.
- Interpretation: a separate native/injection authorization helper exists.
- Confidence: Confirmed static
- Related hypothesis: helper call is proven from `inject()` — not proven; bounded callsite scan is negative.

## 6MR-E04 — generic permission helper

- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:21775-21794`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Observed: `checkCallingOrSelfPermission` followed by `SecurityException`.
- Interpretation: explicit permission enforcement pattern used by selected event-registration methods.
- Confidence: Confirmed static

## 6MR-E05 — service publication

- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:22640-22656`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Observed: Binder endpoint `amazon_input` is published.
- Interpretation: published service name is known; shell/ordinary-app handle availability is not inferred.
- Confidence: Confirmed static

## 6MR-E06 — bounded HOME negative

- Source: `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log:19198-20547`
- SHA-256: `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`
- Observed: no direct HOME resolver/preferred/Fire Launcher token in the BinderService slice.
- Interpretation: input service is not shown as the direct HOME selection writer in this corpus slice.
- Confidence: Strong evidence (bounded)

## Safety disposition

`service call`, guessed transaction codes, `nativeInject*`, input-device access,
ioctl, Accessibility injection, package/settings mutation, Fire Launcher state
changes, Root/exploit execution, OTA/recovery/fastboot, and partition writes
were not performed and remain outside this static closure.
