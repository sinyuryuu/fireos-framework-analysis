# Phase 5H — Level 3 approval report: bounded CMDQ v2/v3 compatibility probe

## Status

**Executed once under explicit approval; completed; no retry.**

Execution result is recorded in
`findings/phase-5h-cmdq-ioctl-result.md` and the raw evidence directory
`adb/phase5/CMDQ-IOCTL-V3-COMPAT-T01-20260803-01/`.

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
4. records only the raw syscall return value (Linux reports a negative
   `-errno` on failure; this freestanding probe does not use libc or read
   `errno`);
5. does not retry, use an address, send another ioctl, or attempt privilege
   changes; and
6. closes the descriptor and exits.

The `count=0` value is selected to exercise the v2 driver's early validation
branch without requesting a DMA buffer. Under the exact source comparison,
the expected discriminator is:

| Driver family | Expected userspace result |
|---|---|
| v2 | raw return `-EINVAL` (normally `-22`), before allocation |
| v3 | raw return `-ENOTTY` (normally `-25`), from the unknown-request path |
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

The command sequence below was executed once under the exact approval. The
reviewed host-built binary and its SHA-256 are recorded below; this does not
authorize any additional execution.

```sh
adb -s G001LT0511550CFT get-state
adb -s G001LT0511550CFT shell id
adb -s G001LT0511550CFT shell getenforce
adb -s G001LT0511550CFT shell mkdir /data/local/tmp/CMDQ-IOCTL-V3-COMPAT-T01
adb -s G001LT0511550CFT push artifacts/phase5/cmdq-compat-probe-build-20260803-03/cmdq_compat_probe /data/local/tmp/CMDQ-IOCTL-V3-COMPAT-T01/probe
adb -s G001LT0511550CFT shell chmod 0700 /data/local/tmp/CMDQ-IOCTL-V3-COMPAT-T01/probe
adb -s G001LT0511550CFT shell /data/local/tmp/CMDQ-IOCTL-V3-COMPAT-T01/probe
adb -s G001LT0511550CFT shell rm -rf /data/local/tmp/CMDQ-IOCTL-V3-COMPAT-T01
```

### Prepared artifact and host-only review

| Item | Value |
|---|---|
| Binary | `artifacts/phase5/cmdq-compat-probe-build-20260803-03/cmdq_compat_probe` |
| Binary SHA-256 | `e0077240040bce55099b8b1b28d9d10723357ef3d3b9640282bd6f6bef2f11fb` |
| C source SHA-256 | `6902bd6aa8e4962ca352fb0c8f51a95509e4530c96b705bf89d93390c688d2d4` |
| AArch64 syscall source SHA-256 | `6ff5d6eff89e85e840bcc27562fd9289d0143cacbeec30c140a071aefc6821b7` |
| Build manifest | `artifacts/phase5/cmdq-compat-probe-build-20260803-03/sha256sums.txt` |
| Static review | `file.txt`, `objdump.txt`, and `disassembly.txt` in the same artifact directory |

The host-only build used `tools/scripts/build_phase5h_cmdq_probe.sh`. That
script does not invoke `adb`, `fastboot`, BROM, DA, or the output binary. The
reviewed disassembly shows the following bounded sequence:

1. AArch64 syscall 56 (`openat`) opens the constant `/dev/mtk_cmdq` path with
   `AT_FDCWD` and `O_RDONLY`.
2. If the descriptor is non-negative, an 8-byte stack request is zeroed as
   `{u32 count, u32 startPA}`.
3. The call site at `0x210344` performs one syscall 29 (`ioctl`) with request
   `0x40087807`, the descriptor, and the zeroed request pointer. There is no
   retry or second ioctl call.
4. The descriptor is closed through syscall 57.
5. The probe writes a short raw-return report through syscall 64 and exits
   through syscall 93. It contains no `mmap`, `ptrace`, `execve`,
   credential-changing syscall, Android API, or returned-address use.

The source, object files, disassembly, ELF metadata, tool versions, and
manifest are retained under the artifact directory above. This is host-only
preparation evidence; it is not evidence of the device's ioctl result.

The executed capture saved before/after shell identity, SELinux state, ADB
state, build fingerprint, verified-boot state, and HOME resolver. It also
saved the probe output, per-command exit codes, and cleanup output. The
temporary directory was the only device filesystem location changed; no
system partition or settings provider was touched. Kernel log capture was not
included in the explicitly approved scope.

The executed run opened the node as fd 3 and returned raw `ioctl_ret=-25`
(`-ENOTTY`). The process exit code was 0 because the probe exits normally
after reporting the raw ioctl result. Cleanup returned 0. The complete
before/after state capture is in the raw evidence directory above.

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

## Approval consumed

The approval for `CMDQ-IOCTL-V3-COMPAT-T01` and binary SHA-256
`e0077240040bce55099b8b1b28d9d10723357ef3d3b9640282bd6f6bef2f11fb` has been
consumed by the single recorded run. It does not authorize any follow-up
ioctl, v3-aware payload, kernel-memory operation, BROM/DA action, or
boot-chain write.
