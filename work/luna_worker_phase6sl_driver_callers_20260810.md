# Phase 6SL — MediaTek/Amazon driver caller join

Date: 2026-08-10  
Target: KFTRWI / trona / MT8183 / PS7331  
Method: host-only source/config/inventory correlation. No device node was opened, no ioctl was issued, no module was loaded, and adb was not used.

## Decision rule

`POSITIVE` requires all four joins: GPL source/config, shipped node or proc
surface, shipped ueventd/init plus SELinux policy, and an exact shipped
userspace caller showing the open/ioctl/proc operation. A source registration,
policy allow, service/process name, package name, or native-library presence
alone is insufficient. No requested surface met all four joins; therefore all
rows below are `UNKNOWN`.

## Caller-join matrix

| Surface | Source/config | Shipped node/proc evidence | Shipped init/ueventd + SELinux | Exact userspace caller | Result |
|---|---|---|---|---|---|
| `/dev/mtk_cmdq` | `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/cmdq/v3/cmdq_driver.c:660-743,864-865`; `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config:1247-1248` | `findings/phase-6rg-report.md:61`; node recorded `0644 system:system`, `mtk_cmdq_device` | `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/selinux/vendor_file_contexts`; `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/selinux/vendor_sepolicy.cil:5228-5229,5754,6087,6199` | No exact shipped native `open("/dev/mtk_cmdq")` plus ioctl caller in `artifacts/phase5/phase5cs-native-analysis-20260804-03/native-inventory.csv` or the native file inventories | UNKNOWN |
| `/dev/ion` | `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/drivers/staging/android/ion/ion.c:1478-1617,1657-1658,1920-1924`; `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config:3532-3534` | No exact `/dev/ion` node line in the shipped read-only node snapshot cited by `findings/phase-6rg-report.md`; node join not established | `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/selinux/vendor_sepolicy.cil:3066,4170,4325,4417` shows policy references, but not a complete shipped caller join | No exact shipped native `open("/dev/ion")` plus ION ioctl caller in the native inventory | UNKNOWN |
| `/proc/perfmgr/perf_ioctl` | `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/performance/perfmgr/perfmgr_main.c`; source mode and creation are summarized in `findings/phase-6qd-privilege-surface.md:38,86` | `findings/phase-6rg-report.md:63`; proc label `proc_perfmgr` recorded, exact mode/caller not established there | `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/selinux/vendor_sepolicy.cil:5229-5230,5286-5287,5304-5305,5902,6204-6205` | Policy names appdomain/bootanim/cameraserver/mediaserver, but native inventory has no exact open/ioctl caller tied to this proc path | UNKNOWN |
| `/proc/m4u` | `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/m4u/2.4/m4u.c:1577-2043,2268`; configuration/branch analysis in `findings/phase-6qd-privilege-surface.md:36-57` | `findings/phase-6rg-report.md:64` records `/dev/m4u` and `/dev/M4U_device` absent; `/proc/m4u` not established in the shipped snapshot | `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/selinux/vendor_sepolicy.cil` exists, but no complete `/proc/m4u` file-context plus caller join was found | No exact shipped native proc reader/writer or ioctl caller found in the native inventories | UNKNOWN |
| RPMB | `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/drivers/char/rpmb/core.c`; `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/drivers/char/rpmb/rpmb-mtk.c`; `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config:2235-2237` | `device/baseline/BASELINE-20260803-05/process_list.txt:166,294` records kernel RPMB thread and `rpmb_svc`; this is not a node/open/ioctl proof | `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/init/rpmb_svc.rc`; `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/selinux/vendor_sepolicy.cil:2380-2381,2474-2475,3056-3057` | `rpmb_svc` process presence is an exact service/process observation, not an exact shipped binary caller operation; no native open/ioctl/proc call was identified | UNKNOWN |
| IDME | `firmware/extracted/PS7331-SOURCE-20250617/platform/device/amazon/kernel/driver/amzn_idme.c:316-347`; `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config:3583-3584` | `adb/phase6n/PHASE6N-KERNEL-RO-20260810-01/amazon_proc_modes.stdout.txt:2-48` records shipped `/proc/idme/*` nodes and labels; this is preserved metadata only | `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/init/fireos.hardware.idme@1.1-service.rc`; `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/selinux/vendor_sepolicy.cil:4471-4473,4741-4749,5135-5137` | IDME HAL/service policy and process evidence identify privileged domains, but no exact shipped userspace proc open/read caller was found in native inventories | UNKNOWN |
| Amazon diagnostics | `firmware/extracted/PS7331-SOURCE-20250617/platform/device/amazon/kernel/driver/amzn_drv_test.c`; conditional production status is documented in `artifacts/phase6nb-amzn-drv-test-source-closure-20260810-02/phase6nb-amzn-drv-test-source.csv` | `findings/phase-6rg-report.md:64` records `/proc/amzn_drvs` absent; `device/baseline/BASELINE-20260803-05/system_packages.txt:196` records `com.amazon.connectivitydiag` | `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/selinux/vendor_sepolicy.cil:4525-4544,5114-5116`; `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/init/fireos.hardware.idme@1.1-service.rc` | Package presence and diagnostic HAL policy do not show an exact native caller opening `/proc/amzn_drvs` or issuing a driver ioctl; no such caller appears in the native inventories | UNKNOWN |

## Negative/unknown boundary

The source tree proves driver entry points and the preserved config proves
selected options, while the image policy proves several privileged domains or
allow rules. Those facts do not identify the userspace call site. The native
inventory is a bounded inventory of shipped ELF files and does not provide an
exact path/function/operation tuple for any requested surface. In particular,
the presence of `com.amazon.connectivitydiag`, `rpmb_svc`, IDME HAL policy, or
an `appdomain` allow must not be promoted to a caller claim.

No `POSITIVE` result is reported. Runtime node metadata and process/package
inventories were used only as existing evidence; this worker performed no
device access.

## Path verification

Every repository evidence path cited above was checked with `test -e`/`test -f`
in the current worktree before report generation. Strings such as `/dev/ion`
and `/proc/m4u` are target-device paths, not local repository paths; their
presence or absence is reported only from the cited shipped snapshot. The two
output files are the only files written by this worker.
