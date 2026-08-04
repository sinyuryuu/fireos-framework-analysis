Phase 5BQ — GhostLock priority and public-route follow-up

This directory records host-side public-source metadata and one fresh
read-only device post-check. It does not contain an exploit payload and does
not authorize or perform a root, bootloader, fastboot, OTA, ioctl, or partition
operation.

Pinned public heads
-------------------
- KoCleo/mtk-easy-su: 8c6871ac7c15b8e98a47e25c35ab93b87e260475
- BaronKiko/LauncherHijack: f79aee3ddd10c053d6d7c55d6f2fc29436001537

The mtk-easy-su README describes a legacy mtk-su/Magisk bootless-root wrapper,
warns that firmware after March 2020 may block the method, and lists no
KFTRWI, trona, or MT8183 target. The local exact-device attempt is already
preserved separately and is not repeated here. LauncherHijack remains a
source-only historical reference; no unknown APK was installed.

Device evidence
---------------
PHASE5BQ-DEVICE-POSTCHECK-20260804-01 is a serial-qualified, read-only ADB
capture. It confirms PS7330.4104N, security patch 2024-02-01, ADB state
device, and HOME resolution to com.amazon.firelauncher/.Launcher. No device
state was changed.

GhostLock boundary
------------------
The exact PS7330 mt8183/4.4 source and the inspected PS7331 source/Image still
show the pre-fix current-task cleanup semantic. The official fix changes the
cleanup and priority-chain task to waiter->task. This is source/inspected-image
evidence, not proof of an exploitable signed PS7330 binary.
