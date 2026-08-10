# Phase 6RX — host-only OOBE/OTA/native lifecycle and broad privilege-sink gap audit

Date: 2026-08-10. Scope is limited to the preserved PS7331 host corpus and
existing read-only captures. No tracked report or README was edited. The row
ledger is [luna_worker_phase6rx_20260810.csv](luna_worker_phase6rx_20260810.csv).

## Bounded result

No new closed ordinary-app/shell-to-sensitive-sink path was identified outside
the Launcher-focused work. The strongest boundaries are:

- `BOOT_AFTER_SYSTEM_OTA` is protected at the action/framework layer. Its
  receiver can enable OOBE and write setup state, but the receiver-local
  permission omission is only a hardening gap; it is not a demonstrated
  low-privilege delivery path.
- Package enable/disable reaches the known PMS protected-package gate for Fire.
  KFT writes are per supplied `UserInfo.id` and are evidenced in child/profile
  lifecycle, not as a User-0 low-privilege writer.
- OTA/recovery native code contains real extraction, block-image, and partition
  write sinks, but no low-privilege caller chain is closed to them.
- Input injection, Amazon package metadata, profile-picker, prewarm, and some
  native/SELinux surfaces retain explicit UNKNOWN gaps. They are not findings:
  a published service, missing local permission marker, native sink, or
  `clearCallingIdentity()` is not caller reachability evidence.

## Status interpretation

`CLOSED` means the reviewed low-privilege path is blocked or the sink is
bounded away from the requested sensitive state. `UNKNOWN` means a specific
caller, permission-holder, user-scope, native enforcement, or consumer artifact
is missing. `RISK-REJECTED` records a deliberately unperformed operation and
must not be read as a negative runtime result.

## Reconciled writer/sink inventory

The CSV covers OOBE/OTA, PMS enable/disable, child/profile creation and state,
settings/DPM, Vending, overlay/native system-server, input, OTA/recovery, and
driver/procfs surfaces. It also records the non-HOME prewarm route because its
identity transition is relevant to broad privilege review.

The only concrete low-privilege confused-deputy evidence in the reviewed
corpus is bounded to non-HOME effects (for example, the known child/profile
settings route and process-prewarm route). No row closes the required chain:

```text
ordinary app or shell
  -> accepted gate
  -> trusted identity transition
  -> package/user/settings/HOME/OTA/native sensitive sink
```

## Safe continuation

Continue only with host-side completion of protected-broadcast manifests,
generated Binder Stub/permission-holder/caller inventories, exact Context/user
resolution, native client plus SELinux domain mapping, and OTA verifier/function
pointer provenance. A natural official OTA may be compared read-only before and
after. Do not manufacture lifecycle events or invoke private interfaces.

## Explicit risk-rejected paths

No unknown Binder transaction, `service call`, private/protected broadcast,
OOBE replay, KFT/profile or DPM mutation, settings/package mutation, input
injection, driver/procfs ioctl, OTA/recovery/updater execution, crafted archive
or traversal input, reboot, root/exploit, remount, SELinux change, overlay
enablement, or partition operation was performed or proposed as a test.

The ledger preserves UNKNOWN rather than inferring vulnerability or safety from
an unclosed artifact.
