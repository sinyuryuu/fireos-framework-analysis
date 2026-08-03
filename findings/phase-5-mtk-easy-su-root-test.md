# Phase 5 — Root-control attempt stopped at warning

## Classification

**已證實：** the verified APK installed and launched on the exact device, but
the Root control was not activated.

**因核准範圍停止：** the first screen was an application warning requiring
an `Accept` action. The approved Level 3 report explicitly prohibited
dismissing a security warning through an unreviewed path, so no UI mutation or
payload execution occurred.

## Observed warning

The UI hierarchy recorded a dialog titled `Warning` with this exact message:

> Misuse of superuser access can seriously damage your device, moreover you
> are fully responsible for your device.

The only visible button was `Accept`. It was not pressed. The Root control was
not reached, and `su -c id` was not run.

## Device result

After the APK was removed:

- package `juniojsv.mtk.easy.su` was absent;
- HOME resolver was `com.amazon.firelauncher/.Launcher`;
- foreground Activity was Fire Launcher;
- ADB remained connected;
- SELinux remained `Enforcing`;
- verified boot remained `green`;
- `ro.boot.flash.locked` remained `1`.

## Evidence

- Test directory: `adb/phase5/MTK-EASY-SU-ROOT-T01/`
- Pre-state: `adb/phase5/MTK-EASY-SU-ROOT-T01-PRE/`
- Post-state: `adb/phase5/MTK-EASY-SU-ROOT-T01-POST/`
- UI hierarchy: `adb/phase5/MTK-EASY-SU-ROOT-T01/window.xml`
- Warning logcat: `adb/phase5/MTK-EASY-SU-ROOT-T01/warning-logcat.txt`
- Rollback output: `adb/phase5/MTK-EASY-SU-ROOT-T01/uninstall.*`

The later device-side observation is documented separately in
`findings/phase-5-mtk-easy-su-root-followup.md` and uses the distinct
`MTK-EASY-SU-ROOT-T02-OBS` evidence directory. It records preflight denials but
does not establish UID 0 or a successful native payload transition.

## Next exact operation requiring approval

If continued, the smallest next Level 3 operation is: reinstall the same
verified APK, launch it, press only the visible `Accept` warning button, then
press the single Root control once, collect only the predeclared observations,
and uninstall immediately. No Magisk approval, boot/system write, Launcher
mutation, or other root command is included.
