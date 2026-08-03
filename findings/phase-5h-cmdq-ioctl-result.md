# Phase 5H — CMDQ v2/v3 compatibility probe result

## Execution record

| Field | Value |
|---|---|
| Test ID | `CMDQ-IOCTL-V3-COMPAT-T01` |
| Serial | `G001LT0511550CFT` |
| Timestamp | `2026-08-03T14:59:16Z`–`2026-08-03T14:59:17Z` |
| Binary | `artifacts/phase5/cmdq-compat-probe-build-20260803-03/cmdq_compat_probe` |
| Binary SHA-256 | `e0077240040bce55099b8b1b28d9d10723357ef3d3b9640282bd6f6bef2f11fb` |
| Raw evidence | `adb/phase5/CMDQ-IOCTL-V3-COMPAT-T01-20260803-01/` |
| Approval scope | One `openat(O_RDONLY)`, one ioctl #7 with `{count=0,startPA=0}`, close, output, cleanup |

The exact approved binary was pushed once, executed once, and removed from
`/data/local/tmp/CMDQ-IOCTL-V3-COMPAT-T01`. No retry, non-zero allocation,
second ioctl, returned-address use, credential operation, memory read/write,
Root setup, or boot-chain command was performed.

## Raw result

```text
open_ret=3 (0x3)
ioctl_ret=-25 (0xffffffffffffffe7)
```

`-25` is the Linux raw syscall representation of `-ENOTTY`. The probe process
exit code was `0` because the small freestanding program reports the ioctl
return value and then exits normally; that process exit code must not be
misread as ioctl success. Stderr was empty, and cleanup returned exit code 0.

## Interpretation

- **已證實（runtime-scoped）：** the normal shell could open
  `/dev/mtk_cmdq` read-only and the installed driver rejected request
  `0x40087807` with raw `-ENOTTY` when the zeroed v2-shaped request was sent.
- **高可信推論：** the installed dispatcher behaves like the exact MT8183
  CMDQ v3 source path that omits ioctl #7 and exposes an unsupported-request
  result. This corroborates the v2 payload/v3 driver mismatch as the reason
  the earlier `MTK-SU-CMDQ-T03` payload stopped at its CMDQ initialization.
- **已證實：** the probe did not obtain Root or alter the Android state. The
  before/after captures retain the same ADB `device` state, shell identity,
  build fingerprint, SELinux state, verified-boot state, and HOME resolver;
  Fire Launcher remained `com.amazon.firelauncher/.Launcher`.
- **未知／未證明：** this result does not prove that every CMDQ v3 path is
  safe, does not establish the absence of another kernel vulnerability, and
  does not establish CVE-2020-0069 exploitability or non-exploitability.

No kernel log was collected as part of the explicitly approved probe scope;
the clean Android postcheck is not a substitute for kernel-log evidence.

## Reproduction

Verify the raw evidence manifest, then inspect:

```sh
shasum -a 256 -c adb/phase5/CMDQ-IOCTL-V3-COMPAT-T01-20260803-01/sha256sums.txt
cat adb/phase5/CMDQ-IOCTL-V3-COMPAT-T01-20260803-01/probe.stdout.txt
cat adb/phase5/CMDQ-IOCTL-V3-COMPAT-T01-20260803-01/probe.exit_code.txt
cat adb/phase5/CMDQ-IOCTL-V3-COMPAT-T01-20260803-01/cleanup.exit_code.txt
```

The device-side operation is complete. Any different ioctl argument, retry,
v3-aware payload, kernel-memory test, BROM/DA operation, or boot-chain action
requires a new exact Level 3 report and approval.
