# Phase 5Y：AEE device-node follow-up

## Why this follow-up exists

Phase 5X 的採樣完整檢查了 process、package、service 與 init path，但當時的
node metadata 只包含 `/dev/sspm`。既有較早的唯讀 `/dev` snapshot 已經出現
`aed0`／`aed1`，因此不能把「沒有 userspace AEE daemon」誤寫成「沒有 AEE
runtime surface」。本 follow-up 只補做 metadata 與 POSIX access check，不開啟
任何 AEE、ATF 或 block device。

Canonical capture：

`adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-06/`

## Exact observations

| Node | Metadata | Shell access check |
|---|---|---|
| `/dev/aed0` | `crw------- root root`, `u:object_r:aed_device:s0`, major/minor `10,60` | `read=0`, `write=0` |
| `/dev/aed1` | `crw------- root root`, `u:object_r:aed_device:s0`, major/minor `10,59` | `read=0`, `write=0` |
| `/dev/atf_log` | `crw------- root root`, `u:object_r:device:s0`, major/minor `10,57` | `read=0`, `write=0` |
| `/sys/class/misc/aed0` | sysfs symlink to virtual misc device | metadata only |
| `/sys/class/misc/aed1` | sysfs symlink to virtual misc device | metadata only |

Process/package/service/init results remain unchanged from Phase 5X:

- kernel threads `[gpu_aee_wq]` and `[mali_aeewp]` are present;
- no userspace process identifiable as `aee`, `aed`, `aee_dumpstate` or an AEE daemon;
- no matching package, Binder service or init service was observed.

The exact Fire source defconfig contains:

```text
CONFIG_MTK_AEE_FEATURE=y
CONFIG_MTK_AEE_AED=y
CONFIG_MTK_AEE_IPANIC=y
CONFIG_MTK_AEE_MRDUMP=y
```

This connects the nodes to an enabled AEE/AED kernel configuration family, but it
does not identify the exact compiled driver implementation or prove that the
MediaTek `CVE-2025-20765` daemon bug exists in the installed PS7330 binary.

## Android implementation boundary

The relevant path is now more accurately represented as:

```text
kernel AEE/AED config
        -> /dev/aed0 or /dev/aed1 (root-only, SELinux aed_device)
        -> vendor AEE daemon, if present and started
        -> crash report / MRDUMP handling
```

The official MediaTek December 2025 bulletin describes `CVE-2025-20765` as a
double-free in the AEE daemon with a race that can cause a system crash and lists
MT8183. It does not provide an Android 9-specific PS7330 binary, a public exact
device PoC, or evidence that the shell domain can reach the daemon.

The device evidence therefore supports:

- **已證實：** AEE/AED kernel configuration and root-only AEE device nodes exist
  on the exact runtime snapshot.
- **已證實：** ordinary shell access checks report no read or write permission for
  the AEE/ATF nodes; no node was opened.
- **Strong evidence：** no userspace AEE daemon endpoint is visible in normal
  process/package/service/init state.
- **待驗證：** exact PS7330 AEE daemon binary, patch status, and kernel-driver
  control flow.
- **已排除：** treating node existence as a shell-readable root primitive.

## Why no live node test was performed

Opening these nodes is not a harmless probe: it enters a vendor driver whose
purpose is crash reporting or secure logging, and its ioctl/read/write contract is
not available from the shell-visible Android interface. A malformed or unexpected
request could cause a system crash, data loss, or reboot without providing a
controlled rollback. The access check and metadata are sufficient to establish
that the current shell cannot use the normal POSIX path.

Accordingly, the following remain **因風險拒絕測試**:

- `open()`/`read()`/`write()`/`ioctl()` on `/dev/aed0`, `/dev/aed1` or `/dev/atf_log`;
- AEE race or malformed daemon input;
- AEE-triggered crash/reboot or MRDUMP path;
- any attempt to change node permissions, SELinux policy or service state.

## Reproducibility

The collector now records `aee_nodes` and `aee_access` in addition to the Phase 5X
runtime fields. It supports `--dry-run` and requires an explicit serial:

```sh
tools/scripts/capture_phase5x_route_surface.sh --dry-run \
  --serial G001LT0511550CFT \
  --test-id PHASE5X-ROUTE-SURFACE-20260804-06 \
  --output adb/phase5/PHASE5X-ROUTE-SURFACE-20260804-06
```

Derived matrix:

- `output/tables/phase5x-aee-node-matrix.csv`
- `artifacts/phase5/public-route-review-20260804-03/candidate-matrix.csv`

## Result for the root research objective

This is a better result than the earlier broad absence statement: the exact
device does expose AEE device nodes, but they are root-only and SELinux-labeled,
and no userspace daemon endpoint is visible. The finding narrows the missing
capability to either an exact PS7330 vendor artifact or a separate privilege
transition; it does not justify a shell trigger or a root claim.

No package, setting, HOME, process, firmware, partition or bootloader state was
changed in this follow-up.
