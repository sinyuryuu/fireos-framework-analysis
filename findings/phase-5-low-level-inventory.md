# Phase 5 — low-level device inventory

## Scope

This phase records the lowest-risk facts that can be obtained while Android is
running normally. It does not enter the bootloader, invoke a MediaTek exploit,
unlock the bootloader, remount a partition, write a partition, or change an
Android setting.

The canonical collections are:

`adb/phase5/PHASE5-LOWLEVEL-BASELINE-20260803-01/`

and the post-root-test read-only recheck:

`adb/phase5/PHASE5-LOWLEVEL-BASELINE-20260803-02/`

Its command list, per-command stdout/stderr/exit code, metadata, summary, and
SHA-256 manifest are retained. The collection script is
`tools/scripts/capture_phase5_low_level_baseline.sh` and refuses an existing
output directory.

## Device state

| Field | Observed value | Evidence |
|---|---|---|
| Model | `KFTRWI` | `device/model.stdout.txt` |
| Product/device | `trona` | `device/product.stdout.txt` |
| Build fingerprint | `Amazon/trona/trona:9/PS7330.4104N/0030099376128:user/amz-p,release-keys` | `device/fingerprint.stdout.txt` |
| Incremental | `0030099376260` | `device/incremental.stdout.txt` |
| Fire OS property | `7.0` | `device/fireos.stdout.txt` |
| Android base | API 28 / Android 9, from the project device baseline | Phase 1–4 evidence and fingerprint |
| Security patch | `2024-02-01` | `device/security_patch.stdout.txt` |
| Board / hardware | `mt8183` / `mt8183` | `device/board_platform.stdout.txt`, `device/boot_hardware.stdout.txt` |
| ADB state | `device` | `adb/devices.stdout.txt`, `adb/get_state.stdout.txt` |
| Verified Boot | `ro.boot.verifiedbootstate=green` | `boot/verifiedbootstate.stdout.txt` |
| Flash lock | `ro.boot.flash.locked=1` | `boot/flash_locked.stdout.txt` |
| Unlocked kernel | `false` | `boot/unlocked_kernel.stdout.txt` |
| RPMB state | `2` | `boot/rpmb_state.stdout.txt` |
| SELinux | `enforcing` | `device/getenforce.stdout.txt` |
| Boot mode | `normal` | `boot/mode.stdout.txt` |
| Preloader build descriptor | `d1a4a4b-20231011_072631` | `device/getprop.stdout.txt` |
| Preloader version | `0x010b` | `device/getprop.stdout.txt` |
| LK build descriptor | `79172a1-20231008_072039` | `device/getprop.stdout.txt` |
| LK version | `0x010a` | `device/getprop.stdout.txt` |
| Boot reason | `wdt_by_pass_pwk` | `boot/bootreason.stdout.txt` |

The device serial used for this collection is `G001LT0511550CFT`. The serial
and exact build are retained in `metadata.tsv`; any future collection must use
an explicit serial and a new test ID.

The second collection recorded the same bootreason and the same Android
identity. The bootreason is retained as metadata only; it is not treated as
evidence of Root, a boot-chain mutation, or a vulnerability.

## Read-only storage observations

The shell-visible `/dev/block/by-name` directory exposes symlinks for `boot`,
`lk`, `recovery`, `system`, `vendor`, `userdata`, `tee1`, `tee2`, and other
partitions. It does **not** expose a `preloader` symlink in this shell listing.
That is only an observation about this directory: it is not evidence that no
preloader exists in boot media.

The mount snapshot shows `/`, `/vendor`, `/system`-backed content, and key
partitions read-only from the shell's view; `/data` is mounted read-write for
normal Android operation. No remount command was issued. The shell could not
read `/proc/cmdline` or `/proc/partitions` (`Permission denied`), and
`/proc/bootconfig` was absent. These failures are preserved, not converted to
“not present”.

## Fire Launcher identity

`pm path com.amazon.firelauncher` returned:

`package:/system/priv-app/com.amazon.firelauncher/com.amazon.firelauncher.apk`

The captured package dump reports:

| Field | Value |
|---|---|
| Version code | `82020310` |
| Version name | `1.3.232663.0_82020310` |
| Code/resource path | `/system/priv-app/com.amazon.firelauncher` |
| Private flags | includes `PRIVILEGED`; also reports partially direct-boot-aware/resizable flags |
| Package flags | includes `SYSTEM` and `HAS_CODE` |
| User 0 state | installed, visible, unsuspended, unstopped, `enabled=0` (default) |
| HOME priority | priority `50` in the captured HOME filters |

This establishes the package's system/privileged placement and HOME filter. It
does not, by itself, establish `persistent`, `coreApp`, system UID, device
owner status, or the source of the PackageManager deny-list membership.

## Host tools

The existing inventory records ADB 1.0.41, Python 3.14.6, JADX 1.5.6, Git
2.40.0, and missing/unusable deodexing and image-writing tools. The Phase 5
collection additionally recorded host `fastboot` 37.0.0-14910828 at
`/opt/homebrew/bin/fastboot`; `fastboot devices` was empty because the tablet
remained in Android mode. No fastboot command was sent to the tablet.

## Firmware compatibility boundary

The repository contains a PS7331 OTA extraction with `mt8183` properties, but
the device under test is PS7330.4104N. The PS7331 files are therefore
`VERSION_MISMATCH` evidence only:

| Artifact | SHA-256 |
|---|---|
| `firmware/extracted/PS7331/images/preloader.img` | `25d8d377d059ec3d5117aa4e749f4f54ef1bfbe8153ae51b309bf20d30eed904` |
| `firmware/extracted/PS7331/images/lk.img` | `1f52e5700058df32ffceeed3fb46d7867f8cc3463286f8177cf17dfcf80de495` |
| `firmware/extracted/PS7331/boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` |

They must not be flashed, used as a recovery set, or treated as proof that a
PS7331 preloader/loader is compatible with PS7330.

## Status

- **已證實：** the exact device is a locked, verified-boot, user/release-keys
  MT8183 tablet running the PS7330.4104N build listed above.
- **已證實：** normal shell access exposes partition names and package paths,
  but not enough boot-chain state to select a safe low-level loader.
- **已證實：** the explicitly approved transition entered fastboot and the
  bootloader reported `product: trona`.
- **已證實：** the bootloader rejected `getvar unlocked`, `getvar secure`, and
  `getvar all` with `the command you input is restricted on locked hw`.
- **待驗證：** the exact preloader revision, DA/SLA/DAA policy, BROM hardware
  identifier, and recovery procedure for this device.
- **高可信推論：** a pinned public MTKClient source provides a meaningful
  MT8183-family lead (`0x6771`/`mt6771_payload.bin`), but its shared SoC alias
  and non-Amazon preloader filenames do not establish PS7330 compatibility.
- **因風險拒絕測試：** BROM/Preloader protocol probes, exploit payloads,
  unlock attempts, and all partition writes. The bootloader transition and the
  four read-only `getvar` queries were executed only after explicit approval;
  their raw evidence is in `adb/phase5/PHASE5-FASTBOOT-GETVAR-20260803-01/`.

See `findings/phase-5-evidence-index.md` for evidence IDs and the complete
file/command mapping. No Level 3 operation has been executed.
