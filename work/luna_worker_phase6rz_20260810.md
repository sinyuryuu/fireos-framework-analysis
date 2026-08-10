# Phase 6RZ — PS7331 GPL kernel / MediaTek / Amazon driver privilege-surface inventory

Date: 2026-08-10 (Asia/Taipei)  
Scope: host-only static review of the extracted PS7331 source, selected config,
boot metadata, existing symbol/string inventories, and saved node/SELinux
metadata. No device node was opened; no ioctl, proc/sysfs/debugfs read/write,
module load, PoC, exploit, reboot, or device mutation was performed.

## Executive result

The source-selected target is KFTRWI/trona, MT8183, Android 9, kernel
4.4.146+, fingerprint `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`.
The canonical Amazon kernel path is `platform/device/amazon/kernel/driver`
and the kernel Amazon staging path is `platform/kernel/.../drivers/staging/amazon`;
an in-tree `drivers/amazon` directory was not found. `platform/vendor/mediatek`
is a separate archive tree and is not, by directory presence alone, proof of
kernel inclusion.

The inventory finds source/config surfaces, but not a demonstrated ordinary-app
privilege transition. Existing runtime evidence proves only shell UID 2000,
`u:r:shell:s0`, enforcing SELinux → read-only `/proc/ged` query telemetry.
That route has no observed PackageManager, Settings, ActivityManager, boot-policy,
or Fire Launcher state edge. All other rows remain source-only, bounded unknown,
or negative at the stated boundary.

## Provenance and interpretation

- Source archive: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar`,
  SHA-256 `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`.
- Build-selected source/config manifest: `kernel/source-manifest.json`;
  source archive SHA-256 `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea`.
- Embedded kernel config: `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config`,
  SHA-256 `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04`.
- Boot image: `firmware/extracted/PS7331/boot.img`, SHA-256
  `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b`;
  unpacked kernel is `firmware/extracted/PS7331/boot_unpacked/Image`.

Source presence, `copy_from_user`, `device_create`, an ioctl table, a permissive
source mode, or SELinux policy allow is not by itself a reachable low-privilege
sink. A caller claim requires an independently preserved client, node policy,
file context/domain, and effect. “Compiled” below means selected by the saved
config or present in the unpacked image/symbol evidence; “source-only” means
the source path exists but final inclusion or runtime reachability is not closed.

## Custom Amazon and MediaTek surfaces

The CSV is the normalized row-level inventory. Key findings:

| Surface | User entry and source path | Static capability / impact | Client and access evidence | Status |
|---|---|---|---|---|
| MTK CMDQ/MDP | `/dev/mtk_cmdq`; `drivers/misc/mediatek/cmdq/v3/cmdq_driver.c:739-741,865,894-898`; MDP `mdp_ioctl_ex.c:332-405,602-729` | `unlocked_ioctl`/compat dispatch; async execution, readback slots, MDP register operations; hardware/display/DMA impact is possible | `CONFIG_MTK_CMDQ=y`, `CONFIG_MTK_CMDQ_TAB=y`; proc debug `status/record/instructionCount` mode `0440`; sysfs attrs owner-only; no in-tree userspace client established; final ueventd/file_contexts/allow mapping absent | Source/config confirmed; caller bounded unknown; no package sink |
| MTK M4U | Active `/proc/m4u`; `drivers/misc/mediatek/m4u/2.4/m4u.c:1577-1809,2220-2270`; debugfs `m4u_debug.c:1505-1539` | MVA allocation, port configuration, monitor, power and translation-fault controls; DMA/IOMMU state impact | Active proc registration is mode literal `0`; `/dev/m4u` misc branch is compiled out by preprocessor; debugfs files mode `0600`; no caller or SELinux mapping preserved | Source-only / access unknown; no package sink |
| MTK performance | `/proc/perfmgr/perf_ioctl`; `performance/perf_ioctl/perf_ioctl.c:69-203,231-232` | write/ioctl/compat handlers for FPSGO/fbc/touch-boost scheduling state | Proc mode `0664` (world-readable, owner/group writable); no local capability check; no client or domain mapping | Writable source surface; reachability unknown |
| MTK accelerometer factory | `/dev/gsensor`; `sensors-1.0/accelerometer/accel_factory.c:35-168,202-227` | `GSENSOR_IOCTL_SET_CALI`, clear/enable calibration; device calibration state | `misc_register`; source node mode unspecified; no `capable()` gate or client found; ueventd/SELinux unknown | Conditional factory surface |
| MTK GED | `/proc/ged`; `gpu/ged/src/ged_main.c:340-344,411` | read/write/ioctl/compat bridge; source includes GPU/DVFS/GE bridge IDs | Saved physical evidence: shell UID 2000, enforcing `shell`, query-only telemetry; source mode `0644`; higher-impact bridge calls were not made | Confirmed shell telemetry only; no privilege/package sink |
| MTK ION | `/dev/ion` plus debugfs; `drivers/staging/android/ion/ion.c:1502-1658,1906-1956`; MTK `ion_drv.c:428-492,703-736` | alloc/free/map/share/import/sync/custom ioctl and debugfs client/heap views; memory/DMA impact theoretical | Saved metadata records mode `0666`, owner `system:graphics`, label `ion_device`; extracted policy allows are not runtime success; bounded 307 APK/JAR scan found no direct client markers; no open/ioctl performed | Source/config and metadata; client/effect unknown |
| MTK RPMB | device created by `drivers/char/rpmb/rpmb-mtk.c:2377-2401,2560-2582,2736-2776` | ioctl and user-copy paths for authenticated replay-protected storage; boot/persistent policy impact theoretically high | `rpmb_svc` is present in saved device properties, but no source-to-service client or node SELinux mapping closes the route; no RPMB operation performed | Source-only / service relationship unknown |
| Amazon lifecycle | `/proc/life_cycle_reason`; `platform/device/amazon/kernel/driver/amzn_sign_of_life.c:255-265,277-370` | proc fops are read/seq only; exported kernel APIs write boot/shutdown/thermal/special reasons | Source mode `0444`; no userspace write callback; `CONFIG_AMZN_SIGN_OF_LIFE=y` and RTC variant selected | Negative for direct userspace write; kernel-call graph remains separate |
| Amazon IDME | `/proc/idme/<field>`; `amzn_idme.c:62-71,319-351` | read-only product/calibration/identity values | fops read-only; permission masking removes write bits; `mac_sec` forces `0400`, uid 1000; no write client | Read-only bounded negative |
| Amazon logger | misc device registered in `amzn_logger.c:698-738` | logger read path and metrics/minerva data; no source package/settings writer | `CONFIG_AMZN_METRICS_LOG=y` and `CONFIG_AMZN_MINERVA_METRICS_LOG=y`; fops read; exact node policy/client not preserved | Read-only/source boundary |
| Amazon driver test | `/proc/amzn_drvs/{sign_of_life,idme,logger}`; `amzn_drv_test.c:747-812` | owner-write decimal dispatcher; index 21 factory-reset lifecycle mode and index 23 RTC special-mode path | source requests `0644`; no capability check; `trona_defconfig` has no `CONFIG_AMZN_DRV_TEST=y/m`; object inclusion/module packaging/final SELinux unknown | High-impact conditional source surface, not shipped-confirmed |
| Amazon liquid detection | sysfs attrs under platform `odm:ld`; `drivers/staging/amazon/amzn_ld.c:638-711,737-786` | store handlers for stop detection, control mode, thresholds, sleep interval; hardware/thermal/USB behavior | attrs declared `0664`; saved runtime audit says no user attributes visible and `/sys/module/amzn_ld/parameters` read denied to shell; no write performed | Bounded negative for saved shell path; final domain matrix incomplete |
| Amazon key combo | input/DT path; `platform/device/amazon/kernel/driver/amzn_keycombo.c:116-158,184-300` | configured key combination can invoke panic/power-off/sign-of-life behavior | no proc/sysfs/ioctl userspace control surface; event source is kernel input/DT; no ordinary client | Kernel/device-event path, not app writer |

## Generic upstream controls kept separate

These are not OEM additions, even when MTK config selects them: `drivers/input/evdev.c:840-892,1324-1331` (`CONFIG_INPUT_EVDEV=y`) exposes generic input read/write/ioctl/compat paths; `drivers/usb/core/devio.c:976-1112,1628-1650,2396-2398` exposes generic USB control/bulk/URB ioctl paths; `drivers/char/mem.c` has the generic `/dev/mem` family but its privileged operations include `CAP_SYS_RAWIO`; and `drivers/char/rpmb` core is generic while `rpmb-mtk.c` is the MTK implementation. No saved userspace client or package/settings/boot-policy sink was established for evdev or USB. These rows are retained in the CSV as `generic-upstream`, not counted as Amazon custom drivers.

## Client, permission, and SELinux boundary

Preserved client evidence is sparse by design. The selected PS7331 framework APK/JAR set is listed by `firmware/extracted/PS7331/selected/extraction-manifest.tsv`, but existing bounded symbol/string inventories did not establish a direct ordinary APK/JAR caller for CMDQ, ION, M4U, RPMB, or Amazon test nodes. The only positive runtime driver caller is the already-saved GED shell query result in `findings/phase-6bq-ged-readonly-ioctl.md` and `adb/phase6bq/PHASE6BQ-GED-RO-20260807-04/`. Saved metadata also records debugfs mounted with `seclabel`; mount presence does not grant a domain access.

Missing or non-equivalent evidence is preserved as unknown: final PS7331 `ueventd*.rc`, exact file_contexts/TE allow joins for every node, generated product `.config` beyond `trona_defconfig`, module packaging/load state, and exact shipped native HAL/service callers. A policy allow or source mode therefore does not become “unprivileged reachable.”

## State-impact conclusion

No row has a source-level edge to PackageManager, SettingsProvider, ActivityManager,
HOME resolver, or Fire Launcher. Amazon driver-test lifecycle/RTC branches could
affect factory/boot state if the feature were built and the proc node authorized;
that is conditional and not confirmed for PS7331 retail. RPMB could carry sensitive
persistent state, and CMDQ/MDP/M4U/ION could affect hardware or memory isolation,
but caller authorization and effect are unresolved. The observed GED route is
telemetry only. Package state, settings state, boot policy, and privilege are
therefore `not demonstrated` by this inventory.

## Safe follow-up boundary

Only host-side joins remain appropriate: exact final image `ueventd`/file_contexts/
TE mapping, product config/Makefile/module provenance, and static caller-to-fops
mapping. Do not open nodes, send ioctls, write proc/sysfs/debugfs, load modules,
or attempt to validate a suspected bug on the device.
