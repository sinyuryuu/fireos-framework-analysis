# Phase 10D2 — driver/caller static closure

Date: 2026-08-10 (Asia/Taipei)  
Scope: host-only static closure over the preserved Phase 7/8 CSVs, PS7331 GPL source, boot/DTB provenance, ueventd/file_contexts/sepolicy/native inventory. No adb, device-node open, read/write/ioctl, debugfs/proc/sysfs mutation, kernel/QEMU, root, or exploit activity was performed. Existing files were not modified.

## Result

The companion CSV records the final join for the prioritized CMDQ/ION/MTK ION/M4U/uinput/AUXADC/Amazon test/liquid/thermal/USB/RPMB surfaces. Each row includes entry, caller, gate, Binder identity, user scope, sink/effect, status, evidence hashes, and the exact missing edge.

All rows remain `UNKNOWN`: the bounded artifacts do not provide a complete shipped caller chain plus final DT/object delivery and merged node policy for any prioritized writable/control path. Source capability, library strings, a policy type, or a source mode is not promoted to a reachable caller. Where the Amazon driver-test gate is negative in `trona_defconfig`, the row is specifically conditional/source-capable rather than shipped-confirmed.

## Closure observations

- CMDQ has partial `/dev/mtk_cmdq` and init/policy provenance; the exact native open+ioctl caller, UID/domain, merged allow tuple, and compiled DTB/object edge are missing.
- ION core and MTK custom paths have `/dev/ion` metadata and config/source evidence. `libion*` markers are capability evidence only; the process-to-ioctl edge, heap/object/DT instance, and final policy remain missing.
- M4U’s active source path is `/proc/m4u`; the `/dev/M4U_device` misc branch is source-disabled by `#if 0` in the cited path. The recorded `system:media 0440` init metadata does not close the proc label/allow or caller identity.
- uinput, AUXADC, liquid-detection, and thermal surfaces expose source-level control registrations, but no shipped writer with UID/domain was recovered.
- Amazon driver-test has a strong build gate: `CONFIG_AMZN_DRV_TEST=y` was not found and the source Kconfig default is `n`. Its factory/RTC effects therefore remain conditional and are not treated as shipped reachability.
- USB devio and RPMB have source/config ABI evidence only; their final node/object/policy and native caller edges are absent.

## Conservative boundary

No row establishes an ordinary-app or low-privilege path to a sensitive sink, and no row establishes a package/PMS/HOME/Settings sink. `UNKNOWN` means the edge was not retained in the supplied static corpus; it does not mean the edge is impossible. Completing closure requires exact variant-matched compiled DTB/object manifests, merged ueventd/file_contexts/TE allow rules, and shipped native/HAL caller relocations with UID/domain provenance.

