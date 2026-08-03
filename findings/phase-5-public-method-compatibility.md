# Phase 5 — public method compatibility review

## Scope

This is a source/provenance review of public methods, not an execution record.
No unknown APK, exploit binary, MTK client, DA, or bootloader command was run
against the tablet.

## Exact device match

The installed device is:

```text
model       KFTRWI
product     trona
SoC         MT8183
Android     9 / API 28
Fire OS     7.3.3.0 / PS7330.4104N
build type  user / amz-p / release-keys
VB          green
flash lock  1
```

Amazon's device specification identifies the Fire HD 10 (2021, 11th
generation) `KFTRWI` as an MT8183, Android 9/API 28, Fire OS 7 device. This
matches the local baseline, but it does not imply that a method for another
Fire generation or another MTK family applies.

## Public method classification

| Method family | Exact-device evidence | Scope | Decision |
|---|---|---|---|
| LauncherHijack / Accessibility | Source reviewed; prior controlled test produced 0/30 foreground handoffs on this build | ADB plus explicit user consent; not formal HOME | Already tested; not a reliable replacement |
| Fire Toolbox launcher options | Historical public reports describe version-dependent launcher reroute/disable behavior; no exact PS7330 low-level unlock | ADB/package state or hijack helper | Do not treat as a bootloader method; no unknown APK execution |
| Generic `mtkclient` BROM/preloader flow | Public source/documentation exists, but inspected BROM config has no MT8183 entry; exact DA/auth/preloader absent | Pre-Android protocol; may read/write or unlock | Compatibility not established; do not run blindly |
| Historical MTK exploits | Chipset-family references exist, but no exact PS7330 preloader/BROM/patch match | Potentially privileged boot-chain access | No candidate is sufficiently matched for execution |
| Standard fastboot unlock | Device reports `flash.locked=1`; fastboot exposure not yet observed | Bootloader state mutation and likely data loss | Only a read-only metadata probe is a possible next step |
| PS7331 OTA images | Same product codename but different build; updater writes boot-chain partitions | Full OTA, including preloader/LK | `VERSION_MISMATCH`; never use as PS7330 recovery |

## Why the historical methods do not close the gap

The local framework evidence explains why the ordinary ADB path fails: Fire OS
adds an Amazon protected-package callback that rejects the shell UID before
Fire Launcher enabled-state mutation. A launcher-hijack helper can observe or
redirect foreground behavior, but it cannot make a third-party package pass
that PackageManager gate or acquire privileged HOME ranking.

The public MTK tool documentation describes BROM/preloader and DA operations,
including read/write and lock-state functionality, but the tool's own source
configuration is the relevant compatibility boundary. The inspected snapshot
contains an MT8168/MT6357 entry and no MT8183 entry. MT8168 is a different
platform. A generic “MTK” label is not enough to select a loader or exploit.

Historical forum/toolbox reports are retained only as leads. They are not
treated as proof of behavior on PS7330.4104N, and no paid/closed-source or
unknown binary is being introduced into the project.

## Determination

- **已證實：** no reviewed public method currently provides an exact,
  reproducible, non-destructive unlock path for this device.
- **高可信推論：** a successful formal HOME replacement requires either a
  privileged/system-signed route, Fire package-state mutation, or a lower-level
  boot-chain compromise; tested shell and Accessibility paths do not provide
  that capability.
- **待驗證：** whether the bootloader exposes a read-only fastboot interface;
  this is the only remaining low-risk information gap before considering any
  lower-level decision.
- **已排除：** treating another MTK chipset's config, an adjacent Fire OTA,
  or historical LauncherHijack behavior as exact-device exploit evidence.
- **因風險拒絕測試：** generic BROM payloads, DA upload, seccfg changes,
  unlock, or partition writes without a matched loader and recovery set.

## References

- Amazon device specification: <https://developer.amazon.com/docs/device-specs/ft-device-specifications-firehd-models.html>
- Amazon current Fire Tablet update page: <https://digprjsurvey.amazon.co.uk/csad/help/node/G2JXLC4L34GX73TE>
- LauncherHijack source: <https://github.com/BaronKiko/LauncherHijack>
- mtkclient source: <https://github.com/bkerler/mtkclient>
- mtkclient BROM configuration: <https://raw.githubusercontent.com/bkerler/mtkclient/main/mtkclient/config/brom_config.py>
