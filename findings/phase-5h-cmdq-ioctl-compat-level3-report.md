# Phase 5H — Level 3 approval report: bounded CMDQ v2/v3 compatibility probe

## Status

**Not approved. Not executed.**

This document proposes one bounded diagnostic operation. It is not a root
attempt and does not propose a kernel-memory primitive. It must not be
expanded into an exploit, retry loop, altered ioctl argument, or BROM/DA
operation without a new report.

## Operation

Test ID: `CMDQ-IOCTL-V3-COMPAT-T01`

From the normal ADB shell context, run a purpose-built, hash-recorded test
program that:

1. opens `/dev/mtk_cmdq` exactly once with `O_RDONLY`;
2. issues exactly one `ioctl(fd, 0x40087807, &request)`;
3. supplies an 8-byte `cmdqWriteAddressStruct` with `count=0` and
   `startPA=0`;
4. records only the return value and userspace `errno`;
5. does not retry, use an address, send another ioctl, or attempt privilege
   changes; and
6. closes the descriptor and exits.

The `count=0` value is selected to exercise the v2 driver's early validation
branch without requesting a DMA buffer. Under the exact source comparison,
the expected discriminator is:

| Driver family | Expected userspace result |
|---|---|
| v2 | `-1`, normally `EINVAL`, before allocation |
| v3 | `-1`, normally `ENOTTY`/unsupported ioctl, from the unknown-request path |
| Vendor variant | Any other result; stop and preserve evidence |

Any success, unexpected errno, hang, kernel warning, or device-state change is
a stop condition. No returned physical address may be printed as usable or
passed to another operation.

## Purpose

The installed kernel's `/proc/config.gz` reports MT8183 and built-in CMDQ, and
the exact Fire source selects v3 for MT8183. T03's payload uses v2 ioctl #7
and failed at initialization. The probe would distinguish the remaining
driver-family uncertainty without trying to allocate a non-zero DMA buffer.

It cannot establish CVE-2020-0069 exploitability and cannot obtain root by
itself.

## Why current ADB-only evidence is insufficient

The current evidence establishes:

- runtime `CONFIG_MTK_PLATFORM="mt8183"`, `CONFIG_MTK_CMDQ=y`, and
  `CONFIG_MTK_CMDQ_TAB=y`;
- `/dev/mtk_cmdq` exists and the shell read check passes while write check
  fails;
- exact Fire source v3 omits ioctl #7; and
- the archived T03 payload failed using ioctl #7.

The remaining unknown is the compiled driver behavior in the installed
kernel. `/proc/cmdline`, `/proc/devices`, `/proc/misc`, dmesg, and the CMDQ
sysfs path are not visible to the shell context. Offline source provenance
cannot by itself prove the running dispatcher.

## Exact proposed command sequence

These commands are proposed only; they were not run. The binary must be
compiled from a reviewed source file and its SHA-256 recorded before the
`adb push` step.

```sh
adb -s G001LT0511550CFT get-state
adb -s G001LT0511550CFT shell id
adb -s G001LT0511550CFT shell getenforce
adb -s G001LT0511550CFT shell mkdir /data/local/tmp/CMDQ-IOCTL-V3-COMPAT-T01
adb -s G001LT0511550CFT push <reviewed-probe-binary> /data/local/tmp/CMDQ-IOCTL-V3-COMPAT-T01/probe
adb -s G001LT0511550CFT shell chmod 0700 /data/local/tmp/CMDQ-IOCTL-V3-COMPAT-T01/probe
adb -s G001LT0511550CFT shell /data/local/tmp/CMDQ-IOCTL-V3-COMPAT-T01/probe
adb -s G001LT0511550CFT shell rm -rf /data/local/tmp/CMDQ-IOCTL-V3-COMPAT-T01
```

The live run would additionally save before/after `getprop`, shell identity,
SELinux state, ADB state, HOME resolver, window/activity state, CMDQ node
metadata, and a bounded logcat window. The temporary directory is the only
device filesystem location changed; no system partition or settings provider
is touched.

## Files or images to be written

- One reviewed test executable to `/data/local/tmp/CMDQ-IOCTL-V3-COMPAT-T01/`.
- No APK, boot image, kernel image, DA, preloader, LK, vbmeta, userdata or
  partition image.

## Target device compatibility

- Serial: `G001LT0511550CFT`
- Model: `KFTRWI`
- Product: `trona`
- SoC: MT8183
- Build: `PS7330.4104N / Fire OS 7.3.3.0`
- Kernel: `4.4.146+`, AArch64
- SELinux: Enforcing
- Verified boot: green
- Bootloader: locked

## Known failure modes

- Shell cannot open the node (`EACCES`).
- Driver returns `ENOTTY`, `EINVAL`, or another error.
- The process blocks in the driver.
- The kernel logs a warning or oopses.
- The device reboots or temporarily loses ADB.
- A vendor variant unexpectedly accepts the request.

## Risk assessment

| Risk | Assessment |
|---|---|
| Soft brick | Low but non-zero; a malformed or vendor-specific ioctl could destabilize the kernel |
| Hard brick | Very low for this bounded no-write probe; no boot-chain interface is used, but cannot be declared impossible |
| Data loss | Low; no userdata/settings/partition write is planned |
| Kernel/DMA side effects | Non-zero; the request is sent to a kernel driver and is therefore not ordinary read-only metadata collection |
| ADB loss | Possible if the kernel hangs or reboots |
| Root obtained | Not expected; this is a compatibility discriminator only |

## Rollback and recovery

Normal rollback is closing the process and removing the temporary directory.
No package state or Android setting is modified. If the device reboots, wait
for ADB to return and compare the saved fingerprint, SELinux state, verified
boot state, HOME resolver, and package state. If ADB does not return or the
kernel repeatedly crashes, stop all further commands and use the device's
normal recovery path; do not automatically fastboot, sideload, erase, or
flash.

## Stop conditions

Stop immediately and do not retry if any of the following occurs:

- ioctl returns success or an unrecognized result;
- the process hangs for the bounded timeout;
- kernel warning/oops, SystemUI failure, reboot, or ADB loss;
- `/dev/mtk_cmdq` permissions differ from the recorded baseline;
- any output suggests a physical address or kernel pointer was returned;
- the test would require a non-zero allocation, a second ioctl, or altered
  input.

## Alternative lower-risk method

Continue offline matching of the PS7330 kernel/driver artifact or obtain
additional exact source provenance. This is preferred if a matching signed
kernel artifact becomes available.

## Approval required

Execution requires explicit approval naming **`CMDQ-IOCTL-V3-COMPAT-T01`** and
the exact reviewed probe binary/hash. Approval for the earlier
`MTK-SU-CMDQ-T03` run does not cover this operation.
