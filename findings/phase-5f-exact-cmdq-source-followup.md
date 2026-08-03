# Phase 5F — exact-source follow-up to `MTK-SU-CMDQ-T03`

## Executive result

The one approved direct `mtk-su64` run failed with exit code `1` and
`Failed critical init step 3`. A host-only disassembly had already mapped that
diagnostic to an ioctl request `0x40087807`. The exact-version Fire HD 10
7.3.3.0 source sample now supplies a more specific, source-scoped explanation:

1. The exact `mt8183_defconfig` selects `CONFIG_MTK_PLATFORM="mt8183"`,
   `CONFIG_MTK_CMDQ=y`, and `CONFIG_MTK_CMDQ_TAB=y`.
2. The exact CMDQ top-level Makefile selects the `v3/` implementation for
   `mt8183`; only `mt6757`, `mt8167`, and `kiboplus` select `v2/`.
3. The exact v3 `cmdq_ioctl()` dispatcher has no
   `CMDQ_IOCTL_ALLOC_WRITE_ADDRESS` case. Its default branch returns
   `-ENOIOCTLCMD` for an unrecognized request.
4. The payload requests the v2 write-address allocation operation, whose
   public/source definition is ioctl number `7`, encoded as `0x40087807`.

Therefore **Strong evidence, source-scoped**: the archived payload expects a
CMDQ v2 write-address interface that is absent from the exact-source MT8183
v3 dispatcher, which plausibly explains the immediate step-3 failure and the
absence of the payload's later root diagnostics. This is not a binary proof:
the installed PS7330 kernel image and its compiled CMDQ object were not
readable in the shell context, and the source archive is an exact marketing
version but not a signed installed-kernel artifact.

## Scope and safety

This follow-up performed no new device mutation. It did not execute the
payload, open `/dev/mtk_cmdq`, issue an ioctl, read or write kernel memory,
reboot, enter fastboot, upload a DA, unlock, remount, or write a partition.
The only device evidence used is the already approved one-shot test
`MTK-SU-CMDQ-T03` and its before/after/rollback records.

The raw 85,000,001-byte HTTP range and the 567,310,765-byte reconstructed
host slice remain outside the public worktree. The public tree retains compact
line-numbered excerpts, hashes, the range metadata record, and the scripts
needed to reproduce the host-only extraction.

## Device and payload evidence

| Item | Observation | Classification |
|---|---|---|
| Device | `KFTRWI` / `trona`, MT8183, PS7330.4104N, Android 9, kernel 4.4.146+, patch 2024-02-01 | **Confirmed** |
| Boot/security state | Verified boot `green`, flash locked, SELinux Enforcing | **Confirmed** |
| Payload | AArch64 `mtk-su64`, SHA-256 `328632e853ff6427af9f35cb83a91d9e960f35d01188ee66d46ae9c7ce7c7827` | **Confirmed** |
| Direct result | Exit code `1`; stderr `Failed critical init step 3`; stdout empty | **Confirmed** |
| Root result | No UID-0 marker; independent shell stayed UID 2000 and Enforcing | **Confirmed / root not obtained** |
| Rollback | Temporary directory removal returned `0`; ADB and HOME remained normal | **Confirmed** |

Primary device evidence is under
`adb/phase5/MTK-SU-CMDQ-T03/`. The original result is
`findings/phase-5e-mtk-su-t03-result.md`; the payload control-flow mapping is
`findings/phase-5e-mtk-su-t03-static-init.md`.

## Exact-source acquisition and reproducibility

Source archive:

`https://fireos-tablet-src.s3.amazonaws.com/7OU0BzzYt2YlM3MKwchLwgyUHM/Fire_HD10-7.3.3.0-20240730.tar.bz2`

The bounded CMDQ range was bytes `2450000000-2535000000`, with 85,000,001
bytes received, curl exit code `0`, 580 independently recovered bzip2 blocks,
and range SHA-256:

```text
d0ae31742da1fff49a5e5a26248b78b52d75b248acbf6939f93092d0ae3041b9
```

The reconstructed tar-slice SHA-256 is:

```text
3eface62137af812ac497ff440b5042cdb3e447b80d83a61fc02f355bf75a6bd
```

The compact source evidence is in
`artifacts/phase5/exact-source-search-20260803/cmdq-source-members-20260803-v5/`
and is verified by its `sha256sums.txt`. The source-range metadata and
host-only reproduction command are in
`artifacts/phase5/exact-source-search-20260803/cmdq-range-2450m-2535m-summary.md`.

The extraction tools are:

- `tools/scripts/scan_phase5_exact_source_cmdq.sh`
- `tools/scripts/extract_phase5_source_members.py`

Both support `--dry-run`; neither invokes ADB or executes source or binary
content.

## Source-level control-flow evidence

### 1. MT8183 selects CMDQ v3

The retained `mt8183_defconfig` excerpt records:

- line 1260: `CONFIG_MTK_PLATFORM="mt8183"`
- lines 1354–1355: `CONFIG_MTK_CMDQ=y` and `CONFIG_MTK_CMDQ_TAB=y`

The retained CMDQ top-level Makefile records:

- lines 15–16: v2 is selected only for `mt6757`, `mt8167`, or `kiboplus`;
- lines 17–19: all other listed platforms use `v3/`.

Since `mt8183` is not in the v2 filter, the exact source build rules select
v3. This establishes the source build selection, not the installed binary's
actual provenance.

Evidence files:

- `cmdq-source-members-20260803-v5/mt8183_defconfig-excerpt.txt`
- `cmdq-source-members-20260803-v5/cmdq_make-excerpt.txt`

### 2. The v3 dispatcher rejects the payload's request family

The exact v3 driver excerpt lists the implemented cases in
`cmdq_ioctl()` at lines 663–706: usage/capability/DTS queries, engine
notification, async execution/wait, and readback slots. The default branch at
lines 700–702 logs an unrecognized ioctl and returns `-ENOIOCTLCMD`.

The compat dispatcher at lines 708–734 likewise has no write-address
allocation or free case. The file operations at lines 738–746 route normal
ioctls to this v3 dispatcher.

Evidence file:

`cmdq-source-members-20260803-v5/v3_driver-excerpt.txt`

### 3. The payload requests v2 write-address allocation

The host-only payload analysis mapped its initialization branch as follows:

```text
0x17d8  call initialization wrapper 0x3300
0x33d8  call allocator helper 0x2f80 with source count 0x3000
0x33e0  zero return branches to failure cleanup
0x34c8  return/diagnostic value -3
```

The helper issues syscall number 29 (`ioctl`) with request
`0x40087807`. The retained v2 header identifies request number 7 as
`CMDQ_IOCTL_ALLOC_WRITE_ADDRESS`; request number 8 is the corresponding free
operation.

Evidence files:

- `artifacts/phase5/mtk-su64-static-init-analysis-20260803/init-allocator-0x2f80-0x30a0.txt`
- `artifacts/phase5/mtk-su64-static-init-analysis-20260803/findings.json`
- `cmdq-source-members-20260803-v5/v2_header-excerpt.txt`
- `cmdq-source-members-20260803-v5/v2_driver-excerpt.txt`

### 4. The v2 path contains the expected allocation contract

For comparison, the exact v2 driver handles
`CMDQ_IOCTL_ALLOC_WRITE_ADDRESS` at lines 709–752, copies the request from
userspace, calls `cmdqCoreAllocWriteAddress()`, and copies the returned address
back. The v2 core validates `count` at lines 8376–8380 and allocates a
`count * sizeof(uint32_t)` hardware buffer at lines 8395–8408.

The v2 header defines:

```text
CMDQ_MAX_WRITE_ADDR_COUNT = PAGE_SIZE / sizeof(u32)
```

at line 117. The payload's initial `0x3000` byte-oriented setup becomes
`0x0c00` 32-bit entries in the observed disassembly; its fallback count is
`0x400`. Thus the v2 source explains why an EINVAL-sized request could have a
retry, while the v3 dispatcher would fail earlier as an unrecognized ioctl.
This is an explanatory comparison, not a new ioctl test.

Evidence files:

- `cmdq-source-members-20260803-v5/v2_core_header-excerpt.txt`
- `cmdq-source-members-20260803-v5/v2_core-excerpt.txt`
- `cmdq-source-members-20260803-v5/v2_driver-excerpt.txt`

## CVE-2020-0069 boundary

The same exact-source v2 core excerpt contains a source-scoped suspicious
bounds check in `cmdqCoreWriteWriteAddress()`:

- line 8508 comments on a 64-bit length;
- line 8510 divides the offset by `sizeof(unsigned long)`;
- line 8523 writes a `uint32_t` at `va + offset`.

This resembles the historical CMDQ write-address issue and is useful for
static triage. It does **not** establish that:

- the installed PS7330 kernel was built from this exact source revision;
- the running driver is v2 rather than v3;
- the relevant ioctl is reachable from shell;
- the historical vulnerability remains exploitable after vendor patches.

The Android security bulletin lists CVE-2020-0069 as a MediaTek System
elevation-of-privilege issue, and the public CTS PoC documents the same CMDQ
device/ioctl family. Those references establish historical scope only. The
device's 2024 patch level is not, by itself, proof of the vendor kernel's
backport state.

## Updated verdicts

| Finding | Status |
|---|---|
| T03 reached the payload's CMDQ initialization failure before root diagnostics | **已證實** |
| `0x40087807` is the write-address allocation ioctl used by the payload | **已證實, source/API-scoped** |
| Exact MT8183 source build rules select CMDQ v3 | **已證實, source-scoped** |
| Exact v3 source dispatcher has no allocation ioctl #7 and rejects unknown requests | **已證實, source-scoped** |
| v3 mismatch is the likely direct reason for this payload's step-3 failure | **高可信推論** |
| The installed PS7330 kernel definitely uses that exact v3 source | **待驗證** |
| CVE-2020-0069 is present or absent in the running PS7330 kernel | **待驗證** |
| This payload obtained root | **已排除（本次 payload/build）** |
| Repeating with altered payload flags, a standalone ioctl probe, or a new kernel-memory primitive | **因風險拒絕測試** |

## Route decision

No new low-risk ADB root route was found. The exact-source result makes an
alternate payload that understands the running CMDQ v3 interface a plausible
research lead, but developing or executing such a payload would be a new
kernel exploit operation. It could involve kernel memory or DMA primitives
and is not covered by the previous one-shot approval. It therefore requires a
new exact Level 3 report and approval before any device execution.

The safe next step is offline acquisition of a matching PS7330 kernel/driver
artifact or additional source provenance. No safe conclusion should be drawn
from the v2 vulnerable-looking code until the running implementation is
matched.

## Public references

- [Android March 2020 security bulletin](https://source.android.com/docs/security/bulletin/2020-03-01?hl=en)
- [AOSP CVE-2020-0069 CTS PoC](https://android.googlesource.com/platform/cts/%2B/1256038a877a81664b7b97448047f03085348fa6/hostsidetests/securitybulletin/CVE-2020-0069/poc.c)
- [Public MediaTek CMDQ v2 driver](https://android.googlesource.com/kernel/mediatek/+/android-mtk-3.18/drivers/misc/mediatek/cmdq/v2/cmdq_driver.c)
