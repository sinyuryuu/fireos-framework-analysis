# Phase 6MT evidence index — Amazon IPC candidate closure

Generated: 2026-08-10
Test ID: `PHASE6MT-STATIC-20260810-01`
Scope: host-only; no device/Binder/ioctl/mutation/reboot.

## 6MT-E01 — proxy-to-implementation mapping

- Source: `decompiled/baksmali/vdexExtractor/boot-fosframework/disassembly.log` and `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` at the candidate ranges recorded in `candidate-summary.csv`.
- Observed: 37 remote methods across 5 interfaces map to service methods; no unmatched proxy method remains.
- Interpretation: interface shape and transaction mapping are reproducible from preserved disassembly.
- Confidence: Confirmed static

## 6MT-E02 — permission and identity matrix

- Source: bounded `BinderService` method blocks in the artifact evidence directory.
- Observed: permission/helper calls, literals, return-value consumption markers, Binder identity calls, and sinks are recorded per method.
- Interpretation: absence of a local marker is an unresolved authorization question, not proof of shell access.
- Confidence: Confirmed static / bounded

## 6MT-E03 — HOME boundary

- Source: all five service ranges.
- Observed: no direct HOME resolver/preferred/Fire Launcher writer token in the candidate slices; activity observation methods are recorded separately.
- Interpretation: these bounded candidates do not close the HOME selection path.
- Confidence: Strong evidence (bounded)

## 6MT-E04 — prewarm permission-result observation

- Source: `fosservices/disassembly.log:40453-40534`, especially `:40473-40474`.
- Observed: `checkCallingPermission("com.amazon.permission.APP_PREWARM")` is
  followed immediately by `Binder.clearCallingIdentity`; the bounded block has
  no adjacent `move-result*` for that check.
- Interpretation: a static authorization anomaly is present, but service
  handle reachability, caller identity, surrounding validation, and impact are
  unresolved. It is not an exploit or HOME replacement finding.
- Confidence: Strong evidence (bounded; not exploit proof)

## Safety disposition

No device command, `service call`, unknown transaction, private API replay,
input injection, package/settings mutation, Fire Launcher state change, Root or
exploit execution, OTA/recovery/fastboot action, or partition write was done.
