# Phase 5E — static mapping of `MTK-SU-CMDQ-T03` init failure

## Scope

This is a host-only, non-executing follow-up to the one approved device test.
The archived AArch64 payload was disassembled and its strings were inspected;
the payload was not executed on the host or device, and no ADB command was
issued by the analysis script.

- Payload: local-only `adb/phase5/MTK-SU-CMDQ-T03/host/mtk-su64`
- Payload SHA-256: `328632e853ff6427af9f35cb83a91d9e960f35d01188ee66d46ae9c7ce7c7827`
- Reproduction script: `tools/scripts/analyze_mtk_su64_init_failure.py`
- Derived evidence: `artifacts/phase5/mtk-su64-static-init-analysis-20260803/`
- Derived manifest verification: `cd artifacts/phase5/mtk-su64-static-init-analysis-20260803 && shasum -a 256 -c sha256sums.txt`

## Precise control-flow result

The direct run emitted `Failed critical init step 3`. The static control flow
maps that number to the following branch:

```text
0x17d8  bl 0x3300
0x17dc  failure test for a negative return
0x1818  load "Failed critical init step %d"
0x1820  negate the helper return for the printed number

0x33d8  bl 0x2f80, with w1 = 0x3000
0x33e0  if w0 == 0, branch to 0x34c0
0x34c8  set w21 = -3
```

Therefore, **Confirmed**: the observed text `step 3` is the `-3` return path
at `0x34c8`, not a report from the later credential, seccomp, or SELinux
patching code. The diagnostic output strings (`UID`, capabilities and SELinux
state) occur later in the wrapper and are unreachable in this failed run.

## What the `-3` path attempts

The helper at `0x2f80` loads a file descriptor from the context, prepares an
8-byte argument at context offset `0x208`, and invokes syscall number 29,
`ioctl`:

| Address | Static observation | Classification |
|---|---|---|
| `0x2fac` | Converts caller `0x3000` to `0x0c00` and stores it as the allocation count | Confirmed |
| `0x2fd0` | Sets syscall number `29` | Confirmed |
| `0x2fc8` / `0x3030` | Uses request `0x40087807` | Confirmed |
| `0x3000`–`0x301c` | On failure, checks `errno == EINVAL` and may retry with count `0x400` | Confirmed |
| `0x3070` | Successful path returns a non-zero requested size | Confirmed |
| `0x2f98` | Failed allocation path returns zero | Confirmed |
| `0x34c0` | Zero from the helper becomes `-3` and frees allocated buffers | Confirmed |

The request decodes as `_IOW(0x78, 7, 8)` (`direction=write`, magic `x`,
number 7, encoded argument size 8). The public MediaTek CMDQ header names
that request `CMDQ_IOCTL_ALLOC_WRITE_ADDRESS`; request number 8 is the matching
free operation used by the cleanup path at `0x3508` and `0x3564`.

This makes the most precise current interpretation:

> **Strong evidence:** the archived payload failed while trying to allocate a
> CMDQ write-address/DMA buffer through `CMDQ_IOCTL_ALLOC_WRITE_ADDRESS`.

It is not correct to claim that the exact driver errno is known: the payload
does not print it on this branch. It is also not correct to claim that this
proves or disproves CVE-2020-0069 in the PS7330 kernel.

## Evidence mapping

| Finding | Evidence |
|---|---|
| Device invocation failed with exit code 1 and exact text | `adb/phase5/MTK-SU-CMDQ-T03/exec/exit_code.txt`, `exec/mtk-su64.stderr.txt` |
| No root marker, ADB state, SELinux, HOME or package state change | `adb/phase5/MTK-SU-CMDQ-T03/comparison/summary.tsv`, `after-exec/`, `after-rollback/` |
| Entry wrapper and printed-step mapping | `artifacts/phase5/mtk-su64-static-init-analysis-20260803/entry-wrapper-0x17a0-0x1924.txt`, `findings.json` |
| Allocation failure branch | `artifacts/phase5/mtk-su64-static-init-analysis-20260803/init-context-0x3300-0x34bc.txt`, `init-allocator-0x2f80-0x30a0.txt` |
| Cleanup request and payload strings | `artifacts/phase5/mtk-su64-static-init-analysis-20260803/cleanup-free-0x34c0-0x35f0.txt`, `strings.stdout.txt` |
| Public ioctl numbering reference | `artifacts/phase5/mtk-su64-static-init-analysis-20260803/public-cmdq-reference.md` |

## Verdicts

- **已證實:** this payload reached an internal CMDQ allocation failure before
  its root diagnostic path.
- **高可信推論:** the failure is caused by incompatibility between this
  archived payload's expected CMDQ allocation behavior and the running
  PS7330 driver, or by the driver refusing the request under the current
  shell/app context.
- **待驗證:** exact errno, exact PS7330 CMDQ validation behavior, and whether
  the historical vulnerability remains exploitable.
- **已排除:** successful root for this payload/build; the prior APK wrapper
  alone is not the only explanation for the direct failure.
- **因風險拒絕測試:** alternate payloads, altered flags/input, standalone
  CMDQ ioctl probes, kernel-memory reads/writes, and BROM/DA/boot-chain actions.
  Each would be a new Level 3 operation requiring a separate exact report and
  approval.

## Public references

- [MediaTek CMDQ driver header](https://android.googlesource.com/kernel/mediatek/+/android-mtk-3.18/drivers/misc/mediatek/cmdq/v2/cmdq_driver.h)
- [Quarkslab CVE-2020-0069 analysis](https://blog.quarkslab.com/cve-2020-0069-autopsy-of-the-most-stable-mediatek-rootkit.html)

