# Phase 5DB — exact PS7331 target and GhostLock evidence chain

Date: 2026-08-04

Scope: current `KFTRWI/trona/MT8183` device, official PS7331 OTA metadata,
official PS7331 source, and the already-preserved PS7331 boot-image marker
analysis. This phase is host-only plus read-only ADB metadata collection. It
does not call futex, create a race, execute an ELF, access kernel memory, or
change the device.

## Executive result

The target identity is now exact rather than inferred:

```text
device fingerprint = OTA post-build fingerprint
device incremental = OTA version_number
device product     = OTA product
device patch       = OTA post-security-patch-level
```

All four comparisons returned `true`. The exact PS7331 source and the
preserved PS7331 boot Image marker set both remain consistent with the
pre-fix `current` cleanup semantics. This is the strongest result currently
available for PS7331, but it is still a static applicability result—not a live
root result.

## Exact target evidence

| Item | Value |
|---|---|
| Device | `KFTRWI` / `trona` / MT8183 |
| Device fingerprint | `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys` |
| Incremental | `0031575863172` |
| Security patch | `2024-08-01` |
| OTA | `firmware/original/update-kindle-Fire_HD10-PS7331_user_4463_0031575863172.bin` |
| OTA SHA-256 | `9f50d2f321f31d2db6bff9bc463cd5faa3597b2fba83d4c35c10ec9d7fbe3cd5` |
| OTA description | Same as device fingerprint |
| OTA type | `full` / block OTA; metadata-only review, not installed by this phase |
| Boot image SHA-256 | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` |
| Exact source SHA-256 | `6cb5442a765b69fa74c8c87b3fa8f44ce1cbb67eec45db3290e512f38eb75dde` |

Raw read-only target capture:

`adb/phase5/PS7331-EXACT-MATCH-20260804-01/`

Manifest SHA-256:
`788c7501a951c4d97e6df649d2db8614daf58e2c8bb0525863a062be3e347cfe`.

## Exact source semantics

The exact build-selected source is:

`firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/kernel/locking/rtmutex.c`

The host-only checker returned:

```text
remove_waiter(): 1079–1129
current->pi_blocked_on = NULL: present
waiter->task cleanup in remove_waiter(): absent
proxy error remove_waiter call: present
classification: PRE_FIX_CURRENT_TASK_CLEANUP_PATTERN
```

Relevant source boundaries:

- `rtmutex.c:952-977`: `task_blocks_on_rt_mutex()` receives the explicit task;
  the self-deadlock return at `972-973` precedes `waiter->task = task` at 977.
- `rtmutex.c:1079-1090`: `remove_waiter()` locks `current->pi_lock` and clears
  `current->pi_blocked_on`.
- `rtmutex.c:1656-1684`: `rt_mutex_start_proxy_lock()` accepts the explicit
  task and reaches `remove_waiter()` on the remaining nonzero path.
- `futex.c:1959-1965`: `futex_requeue()` passes `this->task` into the proxy
  lock API.
- `futex.c:3264-3269`: the PI requeue opcode dispatches into that path.

The fresh exact-source result is stored at:

`artifacts/phase5/phase5db-ps7331-exact-source-semantics-20260804-01/ps7331.json`

## Source-to-Image chain

The preserved boot Image analysis has three sanitized markers:

1. `remove_waiter` obtains the architecture current-task source;
2. it clears a field through that current-task object;
3. the proxy-lock function contains a `remove_waiter` call.

The independent verifier checked the exact target metadata, exact source hash,
boot-image hash, source classification, and all three sanitized markers. Its
result is:

`artifacts/phase5/phase5db-ps7331-exact-chain-verification-20260804-01/verification.json`

```text
exact_ps7331_target_chain_verified = true
source_and_inspected_image_pre_fix_consistent = true
runtime_identity_mismatch_observed = false
runtime_exploitability_proven = false
root_or_privilege_gain_proven = false
```

The Image analysis deliberately contains no runtime address, KASLR slide,
gadget, offset, or payload. The verifier validates preserved markers; it does
not execute the Image or claim that marker presence proves exploitability.

## Userspace and runtime boundary

The existing Fire libc analysis finds ordinary futex wait helpers and a PI-lock
helper, but does not establish a Fire userspace caller for
`FUTEX_CMP_REQUEUE_PI`. The existing bounded runtime capture also did not
observe:

- `waiter->task != current` in one kernel execution;
- `remove_waiter()` executing on the stock device;
- which task/field was cleaned;
- a persistent PI/rtmutex invariant violation;
- a later consumer, memory effect, or privilege transition.

These are separate gates. The exact target match and pre-fix source/Image
chain close the version/provenance gate only; they do not close D1-R through
D4.

## Classification

| Finding | Classification |
|---|---|
| Current device is the official PS7331 target represented by the OTA | **Confirmed** |
| Exact MT8183 PS7331 source retains the pre-fix cleanup semantics | **Confirmed, source scope** |
| Preserved PS7331 boot Image markers are pre-fix-consistent | **Confirmed, sanitized Image scope** |
| PS7331 stock runtime can enter the proxy error cleanup path | **待驗證** |
| Runtime identity mismatch is present | **未觀察** |
| Cleanup residue is persistent or consumable | **未證明** |
| PS7331 can produce temporary root through GhostLock | **未證明** |

## Safe next step

The next useful step is still offline: compare the exact source control flow with
the fixed reference and document the required runtime observations in a
separate instrumented research environment. Repeating ordinary ADB commands
or running a race on the stock tablet would not provide a safe or attributable
proof. A live futex trigger, kernel-memory operation, root payload, unknown
ioctl, boot write, or partition write is intentionally not part of this
phase.

Evidence: `P5DB-E01` through `P5DB-E07` in
`findings/phase-5db-evidence-index.md`.
