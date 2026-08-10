# Phase 6SU — Amazon Framework/System Services IPC residual audit

Date: 2026-08-10 (Asia/Taipei)

This is a host-only, read-only residual audit of the exact-build VDEX/baksmali,
fosinit, manifest/permission, and prior 6SJ–6SQ work products. No adb, Binder or
`service call`, broadcast, settings/package mutation, driver/OTA/recovery action,
root, exploit, or transaction replay was used. Existing files were not modified;
only this report and its CSV companion were added.

## Result

No new evidence-complete ordinary-app/shell → permission/caller → trusted
identity → explicit user scope → package/component state, HOME, settings,
credential, or OTA sink chain was found. The CSV records eight residual static
surfaces. They are **Strong** where a bounded gate and sink are visible but the
caller/identity or downstream consumer is unresolved, and **Unknown** where the
authorization or caller edge itself is not closed.

The strongest residual is `IAmazonPackageManager`: its four mutators check
`amazon.permission.ADD_RM_PKG_METADATA`, accept an explicit user argument, and
reach Amazon flags/metadata storage. 6SJ/6SN establish that the permission is
declared as `signature|privileged` and that `AmazonApplicationFlags.writeToFile`
is a metadata sink; they do not establish the holder/grant, production caller,
or a consumer that writes preferred HOME, component state, or package enabled
state. `registerProxyReceiver`/`deregisterProxyReceiver` remain less complete:
their effective gate and caller identity are not closed.

The DPM row reaches per-user restriction state and includes Binder UID checking
plus an identity-cleared write, but no route to HOME/package state or exact
non-system caller is shown. AMS and WMS rows expose process/display/pinning
sinks, not a Fire Launcher selector. The accessibility row is permission-gated
canvas state with no user/package sink. The profile row confirms a profile
permission boundary and picker-adjacent behavior, not a HOME writer.

The OTA row is limited to the unresolved Java verifier/install → native recovery
caller boundary. It deliberately does **not** repeat the already catalogued
updater partition-write capability. No crafted OTA, recovery execution, or
native transaction was attempted.

## Exclusions and minimal gaps

6SJ–6SQ already close or separately classify the ADD_RM declaration, KFT
child/profile writer, standard PMS/Settings HOME writers, driver/ION capability,
and OTA/updater capability. Those are not promoted here to ordinary-app reachability.

Credential and direct Settings mutation sinks were not found in the bounded
five-interface/service slices. The minimal gap is corpus completeness: an exact
caller/holder/grant join and any omitted/generated/native consumer would be
needed before claiming either a credential/settings route or its absence. No
transaction number is inferred from an unresolved proxy or publication.

## Evidence basis

Primary disassembly hashes carried forward from 6MS are:

* `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` — SHA-256
  `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c`.
* `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` — SHA-256
  `fc101d798368bf91fae1ee553e44964d52bb9e2287652de8c92b43964600ad71`.

The row-level source paths, line/offsets, gates, identity handling, user scope,
and remaining unknowns are in
`work/luna_worker_phase6su_ipc_residual_20260810.csv`.

