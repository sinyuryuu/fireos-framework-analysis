# Level 3 approval report — `mtk-easy-su` Root control test

## Operation

Reinstall the already verified public APK
`juniojsv.mtk.easy.su` (`2.2.1-KoModed2`), launch its `MainActivity`, inspect
the visible UI, and activate the single Root/exploit control once. Capture the
application message, logcat, Activity state, and the result of a read-only
root identity check. Stop immediately after observing the result.

This is a privilege-escalation attempt. It is separate from the completed
download/install/launch/uninstall test in
`findings/phase-5-mtk-easy-su-apk-test.md`.

## Purpose

Determine whether the embedded `mtk-su`/Magisk path produces any useful
compatibility message or temporary root signal on the exact KFTRWI/trona
PS7330.4104N build. No Launcher modification is part of this operation.

## Why current ADB-level methods are insufficient

The shell UID is blocked by Fire OS's protected-package and permission gates.
The APK is the only remaining proposed route in the current evidence that may
change caller authority without changing a system partition. Its compatibility
is unproven and its payload is opaque.

## Exact commands and interaction

The following are the complete proposed steps, in order, using the explicit
serial. The APK hash must be checked before installation:

```text
shasum -a 256 artifacts/phase5/mtk-easy-su-audit-20260803/mtk-easy-su-v2.2.1-KoModed2.apk
adb -s G001LT0511550CFT install --user 0 artifacts/phase5/mtk-easy-su-audit-20260803/mtk-easy-su-v2.2.1-KoModed2.apk
adb -s G001LT0511550CFT logcat -c
adb -s G001LT0511550CFT shell am start -W --user 0 -n juniojsv.mtk.easy.su/.MainActivity
adb -s G001LT0511550CFT shell uiautomator dump /sdcard/window.xml
adb -s G001LT0511550CFT shell cat /sdcard/window.xml
```

After confirming the visible control is the app's Root action
(`MainActivity.kt:146-163` calls `ExploitHandler`), activate that control once
through the visible test UI. Do not activate any other control, dismiss a
security warning through an unreviewed path, or approve Magisk/boot/system
changes.

Immediately after the single activation, collect:

```text
adb -s G001LT0511550CFT logcat -d -b all -v threadtime
adb -s G001LT0511550CFT shell dumpsys activity activities
adb -s G001LT0511550CFT shell dumpsys window windows
adb -s G001LT0511550CFT shell id
adb -s G001LT0511550CFT shell su -c id
adb -s G001LT0511550CFT shell getenforce
adb -s G001LT0511550CFT shell getprop ro.boot.verifiedbootstate
adb -s G001LT0511550CFT shell getprop ro.boot.flash.locked
```

The `su -c id` command is an observation-only identity check; it is not
authorization to run any further root command. No `settings`, `pm`, `mount`,
`dd`, `flash`, `fastboot`, `reboot`, or partition command is included.

## Files or images to be written

- Host: no new APK beyond the already verified release asset.
- Device: normal user APK installation and app-private temporary files created
  by the app; exact payload writes are unknown.
- No image, boot partition, system partition, vendor partition, userdata
  partition, preloader, LK, vbmeta, seccfg, NVRAM, or NVDATA write is proposed.

## Device and firmware compatibility

- Device: Amazon Fire HD 10 11th generation, `KFTRWI` / `trona`.
- Build: `PS7330.4104N`, Android 9/API 28.
- Security patch: `2024-02-01`.
- Kernel: `4.4.146+`.
- SELinux: `Enforcing`.
- Verified boot: `green`.
- Flash lock: `1`.
- Public project: no exact KFTRWI/trona/MT8183 tested entry; project warns
  that post-March-2020 firmware may block the method.

## Expected outcomes

1. Exploit rejected with an app-visible or logcat message; no root.
2. Exploit exits without root; `/sbin/su` remains absent.
3. Temporary root signal; stop after identity capture and do not use root to
   modify Fire Launcher.
4. Unexpected persistent or boot-related behavior; stop and preserve evidence.

## Known failure modes and risks

- Opaque LFS payload may execute commands not recoverable from the source
  review.
- The payload may alter app-private, data, policy, service, or startup state.
- An unexpected reboot, crash loop, ADB loss, or SELinux/verified-boot change
  may occur.
- Uninstalling the APK cannot guarantee reversal of arbitrary payload changes.
- Recovery from persistent changes may require exact firmware/recovery media;
  no such recovery is authorized by this report.

## Stop conditions

Stop immediately, collect current evidence, and do not continue if any of the
following occurs:

- the app requests boot image patching, Magisk installation, bootloader
  unlock, recovery/provisioning reset, factory reset, or partition access;
- an unknown command or binary is requested outside the reviewed app flow;
- ADB disappears, the device reboots unexpectedly, bootloops, or loses the
  normal HOME/UI path;
- SELinux, verified boot, or flash-lock properties change;
- a persistent service, receiver, startup script, or system package change is
  observed;
- the result would require factory reset or flashing to undo.

## Rollback

If the payload does not create persistent changes, the planned rollback is:

```text
adb -s G001LT0511550CFT uninstall juniojsv.mtk.easy.su
```

Then verify package absence, ADB connectivity, build fingerprint, HOME
resolver, Fire foreground, SELinux, verified boot, and flash lock. This is not
a guaranteed rollback for a successful or partially successful root payload.
No factory reset, firmware flash, bootloader operation, or partition write
will be attempted as part of this test.

## Required approval

**Do not execute until the researcher explicitly approves the exact operation
above: one visible Root/exploit activation followed only by the listed
read-only observations and the APK uninstall rollback.**
