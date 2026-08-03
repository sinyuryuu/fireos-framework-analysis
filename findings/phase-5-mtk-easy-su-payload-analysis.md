# Phase 5 — offline payload analysis

## Scope

The exact release APK was inspected offline after the device observation. The
APK digest is:

`a2c509d0b0fcee3bc503bd12986da2d29c74ebcd37abb1af8988f7f26382663d`

The reproducible script is
`tools/scripts/inspect_mtk_easy_su_payload.sh`. It does not install, launch,
or execute any extracted asset.

## Static findings

**已證實：** the APK embeds `mtk-su32`, `mtk-su64`, `magiskinit32`,
`magiskinit64`, `magisk-manager.apk`, and `magisk-boot.sh`. The asset hashes and
file types are preserved in
`artifacts/phase5/mtk-easy-su-audit-20260803/payload-inspection-20260803/`.

**已證實：** the wrapper's Root handler runs ordinary-user preflight commands
before invoking `sh <filesDir>/magisk-boot.sh 32|64`; the JADX control-flow
reference is `W0/c.java` around the command array and `/sbin/su` existence
check. The command sequence includes `getprop ro.vendor.product.model` and
`cat /proc/version`, which matches the denied child-process events in the
follow-up logcat.

**已證實：** the embedded shell script expects a successful temporary-root
transition before its privileged body. It checks `id -u`, requires
`getenforce` to be `Permissive`, invokes `mtk-su`, attempts live Magisk policy
changes, and contains mount/remount and `/sbin` manipulation paths. These
operations were reviewed as text only and were not executed offline or on the
device.

**已證實：** the native asset strings contain `This firmware cannot be
supported` and `Firmware support not implemented`. This is not an exact
KFTRWI/PS7330 compatibility proof, but it is consistent with the observed
failure and the project's post-March-2020 warning.

**已證實：** `file` identifies `mtk-su32` as 32-bit ARM and `mtk-su64` as
64-bit AArch64. It identifies the embedded `magiskinit64` asset as a 32-bit
ARM executable despite its filename; this is an asset-level observation, not
a claim that the wrapper necessarily selects it on this device.

## Runtime interpretation

The follow-up logcat proves that the app reached the preflight stage. It does
not prove that the native `mtk-su` process succeeded. No UID-0 identity,
successful `su -c id`, permissive SELinux state, or confirmed `/sbin/su`
success was captured. Therefore the device-side result remains:

**已證實：** APK preflight reached; no confirmed root.

**高可信推論：** the failure is at or before the temporary-root/Magisk
transition, and the current PS7330/2024-02 locked, green, enforcing build is
not supported by the evidence reviewed so far.

**待驗證：** the native binary's exact return code and the app's final
failure text were not preserved by the follow-up observation. Obtaining those
would require another exact, narrowly scoped Level 3 device test and is not
performed automatically.

## Safety conclusion

No Fire Launcher mutation, partition write, remount, SELinux policy change,
Magisk installation, or host-issued `su` command was performed. A public
payload execution recipe is intentionally not added; the repository contains
hashes, selected static observations, raw device logs, and a no-execution
inspection script instead.
