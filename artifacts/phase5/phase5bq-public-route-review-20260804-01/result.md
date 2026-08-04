# Phase 5BQ result

## Confirmed

- Public `mtk-easy-su` HEAD is
  `8c6871ac7c15b8e98a47e25c35ab93b87e260475`; its README describes the
  legacy mtk-su/Magisk wrapper, warns about firmware after March 2020, and
  does not list KFTRWI, trona, or MT8183.
- Public LauncherHijack HEAD is
  `f79aee3ddd10c053d6d7c55d6f2fc29436001537`; it remains a source reference,
  not a newly installed APK or a formal HOME replacement.
- The fresh read-only post-check remains PS7330.4104N with security patch
  2024-02-01, ADB state `device`, and HOME
  `com.amazon.firelauncher/.Launcher` at effective priority 50.
- Exact PS7330 source and inspected PS7331 source/Image evidence remain
  consistent with the pre-fix GhostLock semantic.

## Strong evidence

- The existing exact-device mtk-su attempt and current public target list do
  not establish a new MT8183/trona route. Re-running the same payload would
  not add a changed prerequisite or a new attribution-quality result.
- PS7331 is an adjacent official full OTA with a newer general security patch,
  but the available GhostLock evidence does not show the `waiter->task` fix.
  Its standalone boot image is not an equivalent update transaction.

## Not performed

No exploit, futex race, kernel memory access, unknown ioctl, root payload,
BROM/DA, preloader/LK operation, fastboot, OTA, reboot, boot write, or
partition operation was performed.
