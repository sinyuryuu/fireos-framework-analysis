# Phase 5G — PS7330 runtime CMDQ corroboration

## Result

The read-only runtime capture materially strengthens the Phase 5F
interpretation. The installed PS7330 kernel itself exposes an embedded
configuration reporting:

```text
CONFIG_MODULES=y
CONFIG_MTK_PLATFORM="mt8183"
CONFIG_MTK_CMDQ=y
CONFIG_MTK_CMDQ_TAB=y
```

The exact-source Makefile selects CMDQ `v3/` for `mt8183`, and the retained v3
dispatcher has no write-address allocation ioctl #7. The runtime evidence
therefore makes the following the current **High-confidence inference**:

> The failed `MTK-SU-CMDQ-T03` payload is using a v2 CMDQ write-address
> contract against a PS7330 kernel built with the MT8183 CMDQ configuration
> whose matching Fire source selects the v3 dispatcher.

It remains **待驗證** whether the installed binary is byte-for-byte derived
from the 7.3.3.0 source archive or contains a vendor backport. No ioctl was
issued to resolve that last uncertainty.

## Runtime capture

Test ID: `PHASE5F-CMDQ-RUNTIME-20260803-02`

- Serial: `G001LT0511550CFT`
- Timestamp: `2026-08-03T14:36:12Z`
- Device state: `device`
- Shell: UID 2000, `u:r:shell:s0`
- SELinux: Enforcing
- Kernel: `Linux 4.4.146+`, AArch64
- Verified boot: green
- Device mutation: none
- Device node open/ioctl: none

Raw outputs and the manifest are under
`adb/phase5/PHASE5F-CMDQ-RUNTIME-20260803-02/`.
The capture script is
`tools/scripts/capture_phase5f_cmdq_runtime.sh`; it requires an explicit
serial, refuses an existing output directory, and supports `--dry-run`.

## Direct runtime observations

### Embedded kernel configuration

`kernel_config.stdout.txt` was obtained by reading `/proc/config.gz` only. The
relevant lines are:

| File / line | Value | Meaning |
|---|---|---|
| `kernel_config.stdout.txt:250` | `CONFIG_MODULES=y` | Kernel supports loadable modules, but this does not mean CMDQ is a module |
| `kernel_config.stdout.txt:1145` | `CONFIG_MTK_PLATFORM="mt8183"` | Runtime kernel platform identity |
| `kernel_config.stdout.txt:1247` | `CONFIG_MTK_CMDQ=y` | CMDQ is built into this configuration |
| `kernel_config.stdout.txt:1248` | `CONFIG_MTK_CMDQ_TAB=y` | CMDQ table support is enabled |

`CONFIG_MTK_CMDQ=y` is distinct from `m`; combined with the exact source's
`obj-y` v3 selection, it is consistent with a built-in v3 driver rather than a
loadable CMDQ module. `/proc/modules` contained only six unrelated modules and
no `cmdq` entry. Module paths under the standard vendor/system locations were
empty in the shell-visible view.

### Device node and IRQs

`cmdq_nodes.stdout.txt` records:

```text
crw-r--r-- 1 system system u:object_r:mtk_cmdq_device:s0 250, 0 /dev/mtk_cmdq
```

The shell could list `/proc/mtk_cmdq_debug`, but reading its `record` and
`status` files was denied. `/proc/mtk_cmdq` was absent. The IRQ snapshot
contains two `mtk_cmdq` entries; IRQ 162 had non-zero counters and IRQ 163 was
present with zero counters. This establishes an active runtime CMDQ surface,
not a successful access to its ioctl API.

The earlier Phase 5E permission check remains authoritative for the shell
boundary: shell read permission passed and shell write permission failed for
`/dev/mtk_cmdq`. No actual `open(2)` or `ioctl(2)` was attempted in either
capture.

### Restricted runtime metadata

The following were retained as failed read-only observations:

- `/proc/cmdline`: `Permission denied`;
- `/proc/devices`: `Permission denied`;
- `/proc/misc`: `Permission denied`;
- `dmesg`: `klogctl: Operation not permitted`;
- `/sys/class/misc/mtk_cmdq`: not visible to the shell context.

These failures are shell/SELinux visibility boundaries. They do not prove
that the corresponding kernel data or sysfs object is absent.

## Source/runtime mapping

| Question | Evidence | Classification |
|---|---|---|
| Is the runtime platform MT8183? | `/proc/config.gz` line 1145; `ro.boot.hardware=mt8183` | **已證實** |
| Is CMDQ enabled in the runtime kernel config? | `/proc/config.gz` lines 1247–1248 | **已證實** |
| Is CMDQ active and exposing the expected character node? | `/dev/mtk_cmdq`, SELinux label, IRQ entries | **已證實** |
| Is the CMDQ driver a separate loaded module? | `CONFIG_MTK_CMDQ=y`; no `cmdq` in `/proc/modules` | **高可信推論：built-in** |
| Does the exact Fire source select v3 for MT8183? | `cmdq/Makefile` lines 14–19 plus defconfig | **已證實，source-scoped** |
| Does exact-source v3 implement payload ioctl #7? | v3 header lines 60–81 and v3 driver lines 663–746 | **已證實，source-scoped：未實作** |
| Is the installed binary exactly that source revision? | No readable kernel image/driver object | **待驗證** |
| Did the T03 payload obtain root? | T03 exit/stderr and post-state | **已排除，本次 payload/build** |

## Low-level route assessment

The runtime evidence does not identify a safe ADB workaround. It instead
narrows the possible low-level work to two materially different questions:

1. **Compatibility-only question:** obtain a matching PS7330 kernel/driver
   artifact offline and verify the v3 mapping without touching the device.
2. **Exploit question:** issue a CMDQ ioctl, adapt the payload to v3, or try a
   different kernel primitive. Any of these can cross into kernel memory/DMA
   access and is a new Level 3 operation. It is not covered by the earlier
   one-shot `MTK-SU-CMDQ-T03` approval.

The current public `mtk-easy-su` README describes a bootless Magisk/mtk-su
wrapper, warns that firmware after March 2020 may block the method, and lists
no KFTRWI, trona, or MT8183 tested result. The linked HackMD list is likewise
not an exact-device lead: its highlighted chains concern Qualcomm Adreno/ABL,
Xiaomi services, or newer Android paths, not this MT8183 Android 9 target.
Those sources are useful triage references, not authorization or compatibility
proof.

## Safety decision

No new exploit, standalone ioctl, kernel-memory read/write, BROM/DA upload,
bootloader unlock, fastboot write, remount, or partition operation was run.

The following remain explicitly rejected until a separate exact Level 3 report
and approval exists:

- standalone `CMDQ_IOCTL_ALLOC_WRITE_ADDRESS` or related ioctl probes;
- altered or v3-aware `mtk-su` payloads;
- kernel-memory/DMA primitives;
- BROM/DA loader or preloader probing;
- seccfg, LK, boot, vbmeta, userdata, or partition writes.

## Evidence paths

- `adb/phase5/PHASE5F-CMDQ-RUNTIME-20260803-02/`
- `artifacts/phase5/exact-source-search-20260803/cmdq-source-members-20260803-v6/`
- `findings/phase-5f-exact-cmdq-source-followup.md`
- `findings/phase-5-evidence-index.md` rows `P5G-CMDQ-001`–`P5G-CMDQ-007`

## Public references

- [KoCleo/mtk-easy-su](https://github.com/KoCleo/mtk-easy-su)
- [User-provided MTK vulnerability index](https://hackmd.io/@lokey0905/rk-hQSzibl)
