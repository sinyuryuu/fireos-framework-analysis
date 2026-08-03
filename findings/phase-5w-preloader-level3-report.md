# Phase 5W — preloader USB candidate Level 3 boundary report

## Decision

**No Level 3 operation is proposed or executed in Phase 5W.** This document records
the boundary so that the adjacent PS7331 static evidence is not mistaken for approval
to interact with the current PS7330 boot chain.

## Operation

Potential future operation: trigger or characterize a MediaTek preloader USB parser
candidate related to CVE-2022-20055／20056.

## Purpose

Determine whether the exact installed PS7330 preloader contains a vulnerable USB
parser and whether an authorized recovery path exists.

## Why current Android-level methods are insufficient

- Android shell cannot read the exact PS7330 preloader/LK image or matching DA.
- The only local image pair is PS7331, while the device reports PS7330/4104.
- The official MediaTek bulletin lists 20055/20056 for MT8183 but Android 10/11/12,
  not the device's Android 9 base.
- A preloader USB test occurs before Android userspace and cannot be represented by
  a normal APK, AOSP framework call, or safe `adb shell` query.
- The adjacent image shows authentication and anti-rollback controls, so a failed
  handshake can have consequences beyond a normal process failure.

## Exact commands proposed

**None.** No BROM/preloader handshake, USB malformed input, DA upload, loader
selection, or image write command is included or authorized by this report.

The only permitted next action under the current evidence is host-only analysis of a
legally obtained exact PS7330 artifact, with hash and provenance verification before
any interpretation.

## Files or images to be written

None. No image, payload, DA, preloader, LK, seccfg, RPMB record or partition file may
be written under this report.

## Target compatibility

| Field | Required | Current evidence |
|---|---|---|
| Device | KFTRWI / trona | confirmed |
| SoC | MT8183 | confirmed |
| Build | PS7330.4104N / 0030099376128 | confirmed |
| Preloader | exact matching PS7330 descriptor/image | not available |
| LK | exact matching PS7330 descriptor/image | not available |
| DA/SLA/DAA | matching authentication policy | unknown |
| Recovery set | verified, device-specific | not available |

## Expected outcome if a future operation were ever separately approved

At most, a version-matched host-side comparison could establish whether a known patch
marker or parser branch differs. It would not imply a root result. A live operation
could instead return an authentication error, remain in a USB download loop, crash or
reboot the boot chain, trigger anti-rollback behavior, or leave the device requiring
authorized recovery.

## Known failure modes

- wrong preloader/LK version or hardware configuration;
- DA/SLA/DAA authentication rejection;
- image signature or anti-rollback rejection;
- USB handshake timeout or bootloader dead loop;
- device reboot or loss of normal ADB state;
- soft brick requiring an exact signed recovery path;
- data loss if a write-capable path is accidentally selected.

## Risk classification

| Risk | Assessment |
|---|---|
| Soft brick | material; exact recovery image and loader are absent |
| Hard brick | non-zero if preloader/seccfg/boot media is written incorrectly |
| Data loss | possible on write/erase path; not acceptable for this phase |
| Rollback / anti-rollback | unknown on PS7330; adjacent PS7331 shows anti-rollback strings |
| Recovery method | not established without exact Amazon-signed artifacts |
| Opening device | may be required if Android/bootloader recovery is unavailable |

## Required backup before any future request

No backup currently in the workspace is sufficient to authorize a boot-chain write.
A future request would need a legally acquired, exact-version recovery set, verified
hashes, a device-specific recovery procedure, and a separate explicit approval. The
PS7331 OTA image is not a backup for PS7330.

## Safer alternatives

1. Obtain an exact PS7330 preloader/LK/vendor artifact from an authorized source and
   compare it offline only.
2. Compare Android 9 AOSP IMS/CTS/ION interfaces with preserved Fire artifacts.
3. Keep CVE-2022-20054 at the existing read-only runtime boundary; do not enable
   ATCI or send modem commands.
4. Keep the tested CMDQ v2 route closed; no alternate ioctl is justified by this
   report.

## Status

- **已證實：** the candidate is a pre-Android boot-chain surface and the local
  PS7331 image is version-mismatched.
- **高可信推論：** an unverified generic loader or parser trigger is unsafe and
  cannot be treated as a reversible Android experiment.
- **待驗證：** exact PS7330 preloader patch state and recovery set.
- **因風險拒絕測試：** all preloader/BROM/DA/USB parser, bootloader, seccfg,
  partition and image-write actions.
