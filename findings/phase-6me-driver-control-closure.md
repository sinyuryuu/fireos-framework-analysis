# Phase 6ME — PS7331 custom-driver control-plane closure

Date: 2026-08-10
Scope: host-only static analysis; no device mutation
Target: KFTRWI / trona / MT8183 / PS7331.4463N / Linux 4.4.146+

## Executive result

This pass answers a narrower question than the existing Phase 6N surface
index: do the selected Amazon/MediaTek/input/power/USB/char driver sources
contain a direct source-level edge to Android `system_server`,
PackageManagerService, ActivityManager/ActivityTaskManager, HOME resolution, or
`com.amazon.firelauncher`?

**Result: 0 direct framework/HOME literal hits in 1,671 selected C/C++/header
files.** The scan found 7,698 bounded source markers, including 1,726 ioctl
markers, 957 user-copy markers, 703 proc/sysfs/debugfs registration markers,
509 device-registration markers, 3 trusted-execution markers, and 3,274
secure-world markers. These are attack-surface markers, not vulnerability
counts.

The strongest supported conclusion is that the custom kernel-driver surfaces
are hardware, telemetry, DMA, secure-world, input, power, USB, or diagnostics
surfaces. They are not shown to be the User-0 HOME or Fire Launcher state
writer. This does not prove every driver is safe or that every production node
has identical runtime policy.

Evidence IDs and hashes are indexed in
`findings/phase-6me-evidence-index.md`; the central scan result is 6ME-SCAN-002
and the normalized rows are 6ME-SCAN-003.

## Evidence classes

### 已證實

- The canonical PS7331 source root is the one recorded in
  `kernel/source-manifest.json`.
- The actual Amazon kernel-driver path is
  `drivers/staging/amazon/`, not `drivers/amazon`.
- The bounded scanner covered the selected custom-driver scopes and recorded
  hashes for every scanned source file.
- No selected source file contains a direct literal/call marker for a
  PackageManager, ActivityManager, ActivityTaskManager, HOME, or Fire Launcher
  sink under the scanner's deliberately narrow patterns.
- The preserved shipped-kernel configuration contains the relevant custom
  surfaces: `CONFIG_MTK_CMDQ`, `CONFIG_MTK_CQDMA`, `CONFIG_MTK_M4U`,
  `CONFIG_MTK_SMI_EXT`, `CONFIG_ION`, `CONFIG_AMZN`, Amazon logging/IDME
  options, and related options in
  `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config:1247-1250,1533,1557,2501,3532,3575-3583`.
- The prior physical GED query-only evidence recorded telemetry access without
  a package, Binder, system-server, or HOME change.

These findings correspond to 6ME-SRC-001/002, 6ME-SCAN-001/002/003/004,
6ME-CFG-001, and 6ME-RUNTIME-001/002.

### 高可信推論

- The observed Fire Launcher enforcement remains a Framework/package-policy
  problem rather than a driver-to-HOME data-flow problem.
- A missing local `capable()` or UID check in an ioctl source file is not enough
  to establish a low-privilege path: Unix node mode, SELinux labels, init
  registration, build configuration, and downstream hardware behavior remain
  separate gates.
- The CMDQ/ION/M4U and secure-world markers warrant defensive review, but they
  do not justify a launcher experiment or a root claim.

### 待驗證

- Exact production reachability and SELinux domain for every indexed node.
- Exact correspondence between selected source functions and every shipped
  kernel binary function.
- CMDQ `addrMetadataCount` arithmetic and downstream use of
  `addrMetadataMaxCount`.
- Whether any secure-world command has an effect relevant to this project;
  this scan found no HOME/PMS source edge.

### 已排除（就目前證據）

- A direct source-level `driver → PMS/ATMS/AMS/HOME → Fire Launcher` path in
  the selected tree.
- Treating GED query success as a launcher or root primitive.
- Treating the existence of an ioctl, `copy_from_user()`, proc/sysfs writer, or
  secure-world marker as proof of exploitability.

### 因風險拒絕測試

No physical CMDQ, ION, M4U, GED write/reset, DMA/readback, debugfs write,
sysfs/module-parameter write, module load, kernel race, panic trigger, root
payload, Binder replay, or partition operation was performed. Those operations
could affect display, DMA, secure-world state, or device availability and are
not needed to answer the bounded control-plane question.

## Exact scope and reproducibility

The scanner reads only source text under these roots of the build-selected
kernel tree:

```text
drivers/misc/mediatek
drivers/staging/amazon
drivers/staging/android/ion
drivers/input
drivers/power/mediatek
drivers/usb
drivers/char
```

It excludes VCS metadata, virtual environments, prebuilt/toolchain/output
directories, and non-source files. It records source SHA-256 values and emits
both per-file closure rows and per-line markers.

Reproduce on the host:

```sh
python3 -m py_compile tools/scripts/audit_phase6me_driver_control_edges.py
python3 tools/scripts/audit_phase6me_driver_control_edges.py --dry-run
python3 tools/scripts/audit_phase6me_driver_control_edges.py \
  --output artifacts/phase6me-driver-control-edges-20260810-01
(cd artifacts/phase6me-driver-control-edges-20260810-01 && sha256sum -c sha256sums.txt)
```

The script does not call ADB, execute binaries, open device nodes, issue
ioctls, or alter the device.

Inputs and outputs:

- Scanner: `tools/scripts/audit_phase6me_driver_control_edges.py`
- Normalized table:
  `output/tables/phase6me-driver-control-closure.csv`
- Marker detail:
  `artifacts/phase6me-driver-control-edges-20260810-01/driver-control-markers.csv`
- Hashes:
  `artifacts/phase6me-driver-control-edges-20260810-01/source-hashes.tsv`
- Summary:
  `artifacts/phase6me-driver-control-edges-20260810-01/summary.json`
- Call graph:
  `output/call-graphs/phase6me-driver-control-closure.mmd`
- Worker scope review:
  `work/luna_worker_kernel_surface_followup_20260810.md`

## Static call/data-flow model

```text
source file
  → driver/proc/sysfs/device registration
  → fops / ioctl / user-copy boundary
  → local capability/UID/SELinux-related markers (if present)
  → hardware / telemetry / DMA / secure-world candidate
  -X→ Android system_server / PMS / AMS / ATMS / HOME / Fire Launcher
```

The negative edge is a bounded source-text result, not a whole-system formal
proof. Kernel-to-userspace communication can also occur through events,
properties, files, or vendor-specific interfaces not represented by a direct
literal in the selected C/H source. Those require separate provenance and
runtime evidence.

## Important source locations

The following are retained as review anchors rather than exploit instructions:

- CMDQ dispatcher and file operations:
  `drivers/misc/mediatek/cmdq/v3/cmdq_driver.c:660-743`.
- CMDQ secure metadata path:
  `drivers/misc/mediatek/cmdq/v3/cmdq_driver.c:359-405`.
- ION ioctl/compat surface:
  `drivers/staging/android/ion/ion.c:1478-1617,1657-1658`.
- GED proc/ioctl surface:
  `drivers/misc/mediatek/gpu/ged/src/ged_main.c:271-346,407-416`.
- Amazon IDME/logger/sign-of-life sources:
  `drivers/staging/amazon/` plus the corresponding Amazon device-tree driver
  sources recorded by Phase 6N.
- Shipped config anchors:
  `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config`.

## Runtime correlation

The existing exact-build evidence remains authoritative for runtime claims:

- `adb/phase6bq/PHASE6BQ-GED-RO-20260807-04/` — read-only GED query path;
  no HOME/package mutation.
- `adb/phase6n/PHASE6N-KERNEL-RO-20260810-01/` — shell identity, enforcing
  SELinux, node metadata, and HOME remained Fire priority 50.
- `findings/phase-6ha-p5-driver-reaudit-ged-cmdq-boundary.md` — CMDQ malformed
  path was not exercised; GED write/reset paths were not called.
- `findings/phase-6is-selinux-driver-route-closure.md` — no demonstrated
  shell-to-driver-to-Framework/HOME edge.

The source scan intentionally does not upgrade `runtime_reachability`; its
table value is `not-derived-from-source`. This prevents a source registration
from being mistaken for a live device node or an accessible SELinux route.

## Disposition

This phase closes one additional lower-layer hypothesis for the launcher
objective: the selected custom-driver source does not expose a direct HOME or
PackageManager sink. It does **not** close the independent question of whether
an unrelated kernel or secure-world vulnerability exists, and it does not
support executing an exploit. The highest-value remaining launcher work is
therefore still the trusted Android Framework/User-0 state path or a measured,
user-authorized foreground fallback; hardware-facing ioctl testing should not
be reopened merely because the source contains many user-copy operations.
