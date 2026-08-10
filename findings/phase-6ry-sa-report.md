# Phase 6RY–SA — IPC, kernel-driver, and official-update surface review

Date: 2026-08-10
Device: PS7331.4463N / KFTRWI / trona / Android 9 API 28
Public baseline: `80fb5c6fe`

## Executive result

This round broadens the search beyond Launcher and combines 45 host-only ledger
rows with one exact-serial read-only device snapshot:

| Scope | Rows |
|---|---:|
| Amazon permission/IPC provenance | 12 |
| MediaTek/Amazon/upstream kernel and driver surfaces | 16 |
| Official 7.3.3.1 update-package provenance | 17 |
| **Total** | **45** |

The evidence confirms high-privilege capabilities, but does not close an
ordinary-app or shell path to those capabilities. No Root, exploit, private
Binder transaction, driver operation, OTA execution, or partition write was
performed.

## Device evidence — 已證實 / Confirmed

The new exact-serial snapshot (`G001LT0511550CFT`) confirms:

- PS7331.4463N / Fire OS 7.3.3.1 / Android 9 API 28;
- SELinux Enforcing and shell context `u:r:shell:s0` with UID 2000;
- HOME resolver `com.amazon.firelauncher/.Launcher`, effective priority 50;
- Microsoft Launcher remains a candidate at priority 0;
- visible node metadata includes `/dev/mtk_cmdq` (`0644 system:system`),
  `/dev/gsensor` (`0660 radio:system`), and `/proc/perfmgr/perf_ioctl`
  (`0664 root:root`); no node was opened or read for driver data.

This snapshot is observation, not a privilege test. The node mode and SELinux
label alone do not prove a usable ioctl or package-state effect.

## 6RY — permission and IPC provenance

`IAmazonPackageManager` transactions 1–5 and `AmazonPackageManagerService`'
four metadata/flags mutators are statically mapped through
`checkCallingOrSelfPermission("amazon.permission.ADD_RM_PKG_METADATA")` to
`AmazonApplicationFlags` XML persistence. The exact declaration/grant/holder
and production caller remain `UNKNOWN` in the bounded PS7331 corpus. Generated
Stub/Proxy code is an IPC contract, not a caller.

The visible consumers are package recency, game-mode, and compatibility
classification. No edge to `setHomeActivity`, preferred-activity APIs,
`setApplicationEnabledSetting`, or `setComponentEnabledSetting` was found in
the reviewed corpus. Standard permissions such as
`CHANGE_COMPONENT_ENABLED_STATE`, `MANAGE_USERS`, `WRITE_SECURE_SETTINGS`, and
install/delete permissions are recorded separately; a holder row is not proof
that the package was the caller or reached the Fire target.

**判定：高可信推論 / Strong evidence** for a metadata-only bounded sink;
**待驗證 / Pending** for the exact holder, production caller, and unreviewed
consumers. No confused-deputy claim is made.

## 6RZ — kernel and driver inventory

The official source places Amazon kernel code under
`platform/device/amazon/kernel/driver` and staging code under
`platform/kernel/.../drivers/staging/amazon`; no in-tree `drivers/amazon`
directory was found. The inventory separates source/config capability from
runtime reachability:

- **CMDQ/MDP**: ioctl/compat and hardware/display/DMA paths exist in source;
  no userspace client or package/settings sink is established.
- **ION**: source/config and saved metadata show `/dev/ion` mode 0666,
  `system:graphics`, `ion_device`; no open/ioctl was performed and no client or
  privilege sink was closed.
- **Performance procfs**: `/proc/perfmgr/perf_ioctl` has a source write/ioctl
  surface; live metadata is root-owned `0664`, so mode alone does not show shell
  write access. Client and effect remain unknown.
- **M4U/RPMB**: high-impact source paths exist, but exact shipped node policy,
  client, and caller are unresolved; `/dev/m4u` and `/proc/amzn_drvs` were not
  present in the saved live node metadata.
- **Amazon driver test**: source includes high-impact test indices, but
  `trona_defconfig` lacks `CONFIG_AMZN_DRV_TEST=y/m`; this is a conditional
  source path, not shipped-device evidence.
- **Amazon IDME/sign-of-life/logger/key-combo**: reviewed paths are read-only or
  kernel/DT event paths; no ordinary userspace package-state sink was found.
- **GED/gsensor/liquid detection**: bounded telemetry or hardware-calibration
  surfaces; no package/HOME/privilege transition was shown.

**判定：已證實 / Confirmed** for source/config and selected metadata facts;
**待驗證 / Pending** for final ueventd/file-context/TE/client joins;
**因風險拒絕測試 / Risk-rejected** for opening nodes, ioctl, procfs/sysfs/
debugfs writes, module loading, or kernel PoC execution.

## 6SA — official 7.3.3.1 update package

The preserved official signed OTA is a 27-member ZIP with metadata matching
trona/PS7331. The static chain is:

```text
signed OTA
  -> metadata/product/version/PVT/device checks
  -> RecoverySystem verification
  -> privileged SideloadMover / UpdateSystem.install
  -> recovery update-binary / Edify handlers
  -> fixed extraction or block-image targets
  -> partition write capability
  -> guarded BOOT_AFTER_SYSTEM_OTA
  -> OOBE component/setup-state sinks
```

This proves capability and gates, not a low-privilege caller. Java staging uses
basename/rename/copy/delete behavior and lacks a visible canonical/NOFOLLOW
marker; native code contains readlink-family markers. These are static
sensitivity points only. No crafted filename, symlink, traversal, malformed
package, updater, recovery, install, reboot, or partition action was run.

The worker summary said 18 rows, but the preserved CSV has 17 data rows and 9
columns; the normalized matrix uses the actual parsed file count and records
the worker files unchanged.

**判定：已證實 / Confirmed** for official artifact hashes and privileged
update capability; **高可信推論 / Strong evidence** for the absence of a
closed ordinary caller in the reviewed chain; **待驗證 / Pending** for outer
archive EOF, native indirect dataflow, and exact delivered OOBE user mapping.

## Unified conclusion

The current evidence supports this boundary:

```text
ordinary app / shell
       |
       +--> permission/user/SELinux gate --X--> Amazon metadata or package sink
       |
       +--> driver node metadata ----------?--> hardware/DMA/control capability
       |
       +--> OTA staging/verification ------X--> recovery/partition writer

system/privileged lifecycle ------------------> package/OOBE/partition capability
```

The only known path that can alter Fire package state is still a trusted,
user/profile-scoped or system-server path. This round found no safe ADB-level
privilege elevation and no new formal HOME replacement. The best no-root
alternative remains the previously measured, user-consented Accessibility
foreground redirect; it does not grant privilege or disable Fire Launcher.

## Safety and remaining work

Not executed: Root/exploit payloads, unknown Binder/service transactions,
private/protected broadcasts, driver open/ioctl, procfs/sysfs/debugfs writes,
OTA/recovery/updater execution, crafted archive testing, reboot, remount,
SELinux changes, or partition writes.

The remaining safe research value is limited to offline provenance: exact
permission-grant source, final ueventd/SELinux/client joins, outer archive EOF,
and native indirect-call dataflow. If those do not close an ordinary caller to
a sensitive sink, formal HOME replacement and low-privilege Fire disabling
should be considered unavailable on this build without higher privilege.

## Artifacts

- `findings/phase-6ry-sa-report.md`
- `findings/phase-6ry-sa-evidence-index.md`
- `output/tables/phase6ry-sa-control-surface.csv`
- `output/tables/phase6ry-sa-control-surface.csv.manifest.json`
- `output/call-graphs/phase6ry-sa-control-surfaces.mmd/.md`
- `tools/scripts/build_phase6ry_sa_surface.py`
- `adb/phase6ry/PHASE6RY-DEVICE-READONLY-20260810-01/`
