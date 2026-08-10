# Phase 6SO — native driver-caller provenance closure

Date: 2026-08-10  
Target: PS7331 / MT8183 / trona / Fire OS 7.3.3.1

This is a host-only static join. No device node was opened, no ioctl or proc
operation was issued, no ELF was executed, and no adb/device action was
performed.

## Rule and result

`POSITIVE` requires all four joins: (1) exact-build GPL source and selected
config, (2) shipped node/proc or equivalent shipped device surface, (3)
shipped init/ueventd/file-context/SELinux policy, and (4) an exact shipped
native ELF caller with a path-specific open/proc operation and, where
applicable, an ioctl call site. A library-level caller is explicitly labeled
as such; it does not prove that a particular top-level process invoked it.

Under that rule, ION is `POSITIVE — shipped native library caller` because the
preserved shipped `/system/lib64/libion.so` and `/vendor/lib64/libion_mtk.so`
contain the `/dev/ion`/`ion_open`/`ioctl` evidence and disassembly-backed ION
request sites. All other requested surfaces are `UNKNOWN / Not established`:
their source/config and some node/policy evidence exist, but no exact shipped
native ELF operation joining that surface was found.

## Per-surface evidence matrix

| Surface | Exact-build GPL source + config | Shipped node/proc evidence | Shipped policy/init evidence | Native ELF strings/symbols/relocations/call sites | Result and gap |
|---|---|---|---|---|---|
| `/dev/mtk_cmdq` | `firmware/extracted/PS7331-SOURCE-20250617/platform/kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/cmdq/v3/cmdq_driver.c:660-743,864-865`; `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config:1247-1248` (`CONFIG_MTK_CMDQ=y`, `CONFIG_MTK_CMDQ_TAB=y`) | `findings/phase-6rg-report.md:61` records `crw-r--r-- system:system`, `mtk_cmdq_device` | `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor/etc/selinux/vendor_file_contexts`; `vendor_sepolicy.cil:5228-5229,5754,6087,6199` | Phase 5 native inventories have no exact shipped ELF string/symbol/call-site tuple for `open("/dev/mtk_cmdq")` plus CMDQ ioctl. The archived CTS/probe is a test artifact, not a shipped product caller (`artifacts/phase5/android-cmdq-implementation-review-20260804-01/comparison.json`) | `UNKNOWN / Not established`; native caller join missing |
| `/dev/ion` (ION core) | `.../drivers/staging/android/ion/ion.c:1478-1617,1657-1658,1920-1924`; `kernel.config:3532-3534` (`CONFIG_ION=y`, `CONFIG_MTK_ION=y`) | `artifacts/phase5/phase5bl-futex-gates-analysis-20260804-01/observations.csv:6` records `/dev/ion`, `system:graphics`, mode `0666`, `ion_device`; `phase5cs-native-inventory.../system-lib64.txt:282` lists shipped `libion.so` | `artifacts/phase6c/phase6c-image-policy-extract-20260804-06/vendor_sepolicy.cil:3066,4170,4325,4417`; node label is also preserved in the Phase 5 metadata | `artifacts/phase5/mtk-ion-static-analysis-20260804-03/libion.so.strings.txt` contains `/dev/ion`; `libion.so.nm-D.txt` exports `ion_open`, `ion_alloc`, `ion_map`, `ion_share`, `ion_import`, `ion_sync_fd`; `ioctl-call-sites.tsv` records `ion_alloc@0xbd8` (`ION_IOC_ALLOC`), `ion_map@0xe00` (`ION_IOC_MAP`), `ion_share@0xff8` (`ION_IOC_SHARE`), `ion_import@0x13a8` (`ION_IOC_IMPORT`), and `ion_sync_fd@0x1490` (`ION_IOC_SYNC`). | `POSITIVE — shipped native library caller`; remaining gap is the top-level process/library consumer and runtime invocation, not the static library-to-node/ioctl join |
| `/dev/ion` (MTK custom ION) | Same exact ION source/config; MTK implementation `.../drivers/staging/android/ion/mtk/ion_drv.c:428-492,703-736` | Same `/dev/ion` shipped node and `/vendor/lib64/libion_mtk.so` (`phase5cs-native-inventory.../vendor-glob.txt:313`) | Same extracted vendor CIL references above | `libion_mtk.so.nm-D.txt` exports `mt_ion_open`, `ion_custom_ioctl`, cache/DMA helpers and imports `ioctl`; `ioctl-call-sites.tsv` records `mt_ion_open@0xc0c` and custom call sites at `ion_alloc_camera_pool@0xd74`, `ion_custom_ioctl@0xe90`, `ion_cache_sync_flush_range@0x112c`, `ion_dma_map_area@0x131c`, and related VA/map/unmap sites as `0xc0104906` (`ION_IOC_CUSTOM`). | `POSITIVE — shipped native library caller`; top-level consumer and runtime call remain unknown |
| `/proc/perfmgr/perf_ioctl` | `.../performance/perf_ioctl/perf_ioctl.c:69-203,231-232`; source proc mode `0664`, fops include write/ioctl/compat; config support summarized in `findings/phase-6qd-privilege-surface.md:38,86` | `findings/phase-6rg-report.md:63` records `proc_perfmgr` label; exact shipped owner/mode join is not complete there | `vendor_sepolicy.cil:5229-5230,5286-5287,5304-5305,5902,6204-6205`; these are policy references, not a caller | No exact shipped ELF string/relocation/symbol/call-site tuple for `/proc/perfmgr/perf_ioctl` open/write/ioctl. `libperfctl*` presence in inventory is name/presence only | `UNKNOWN / Not established`; proc caller and final ownership join missing |
| `/proc/m4u` | `.../m4u/2.4/m4u.c:1577-2043,2268`; active proc path; `/dev/m4u` misc branch is preprocessor-inactive (`findings/phase-6qd-privilege-surface.md:36-57`) | `findings/phase-6rg-report.md:64` records `/dev/m4u` and `/dev/M4U_device` absent; `/proc/m4u` not established in that shipped snapshot | No complete final `/proc/m4u` file-context + init/SELinux + caller join in the preserved policy; source mode literal `0` is not access proof | No exact shipped native proc reader/writer or M4U ioctl ELF caller in the native inventories | `UNKNOWN / Not established`; shipped proc and native caller joins missing |
| `/dev/m4u` and `/dev/M4U_device` related nodes | Source contains the inactive misc-device branch in the same M4U file; active product path is `/proc/m4u` | Shipped snapshot explicitly records both device nodes absent (`findings/phase-6rg-report.md:64`) | No shipped node policy can close an absent node; no complete proc policy join either | No native ELF caller; no `open`/ioctl evidence for either path | `UNKNOWN / Not established`; source presence must not be promoted to shipped reachability |
| RPMB (`/dev/rpmb*`/RPMB char path) | `.../drivers/char/rpmb/core.c`; `.../drivers/char/rpmb/rpmb-mtk.c`; `kernel.config:2235-2237` (`CONFIG_RPMB=y`, `CONFIG_RPMB_INTF_DEV` and SIM unset) | `device/baseline/BASELINE-20260803-05/process_list.txt:166,294` and `identity.txt` record `rpmb_svc`/RPMB threads; this is not a node/open/ioctl proof | `artifacts/phase6c/.../vendor/etc/init/rpmb_svc.rc`; `vendor_sepolicy.cil:2380-2381,2474-2475,3056-3057` | No exact shipped native ELF `open`/ioctl caller for an RPMB node or a service-to-driver call site. Preloader RPMB strings are bootloader evidence, not a shipped Android native caller | `UNKNOWN / Not established`; node and service-to-driver native caller gap |
| IDME `/proc/idme/*` | `.../platform/device/amazon/kernel/driver/amzn_idme.c:316-347`; `kernel.config:3583-3584` (`CONFIG_AMZN_IDME=y`); source read/seq path strips write bits | `adb/phase6n/PHASE6N-KERNEL-RO-20260810-01/amazon_proc_modes.stdout.txt:2-48` records shipped `/proc/idme/*` nodes/labels as preserved metadata | `.../vendor/etc/init/fireos.hardware.idme@1.1-service.rc`; `vendor_sepolicy.cil:4471-4473,4741-4749,5135-5137` | Native inventory lists `fireos.hardware.idme@1.0/.1.so` (`vendor-glob.txt:12-13`) but no exact `/proc/idme` string plus open/read call site or relocation chain | `UNKNOWN / Not established`; HAL presence is not a proc reader proof; write route is source-bounded negative |
| IDME block/HAL related device path | Same IDME source/config; block label and HAL path are covered by `findings/phase6sg_driver_join_20260810.md:30` | Shipped block-node owner/mode is not closed in the preserved snapshot | CIL/HAL/init evidence exists, but not a complete block owner/mode + native operation join | No exact shipped native HAL-to-IDME-block `open`/read/write call site in the available ELF inventories | `UNKNOWN / Not established`; native HAL-to-block edge missing |
| Amazon diagnostics `/proc/amzn_drvs/*` | `.../device/amazon/kernel/driver/amzn_drv_test.c`; `artifacts/phase6nb-amzn-drv-test-source-closure-20260810-02/phase6nb-amzn-drv-test-source.csv`; `trona_defconfig` lacks `CONFIG_AMZN_DRV_TEST=y/m` | `/proc/amzn_drvs` absent in `findings/phase-6rg-report.md:64`; `device/baseline/BASELINE-20260803-05/system_packages.txt:196` records `com.amazon.connectivitydiag` only | `vendor_sepolicy.cil:4525-4544,5114-5116` and IDME HAL init are not proof that the test proc exists or is callable | No exact shipped native ELF caller for `/proc/amzn_drvs`; package presence has no native proc open/write call-site evidence | `UNKNOWN / Not established`; conditional source only, shipped node and caller missing |
| Related Amazon logger nodes `/dev/metrics`, `/dev/vitals` | `.../device/amazon/kernel/driver/amzn_logger.c`; read/poll/release only, no write (`work/luna_worker_phase6mz_driver_inventory_20260810.md:51`) | Source/documentation establishes names; saved node/policy join for this target is incomplete | No complete shipped ueventd/file-context/SELinux + native caller join in the preserved reports | No exact shipped native ELF open/read/poll caller identified; native library/process names alone are insufficient | `UNKNOWN / Not established`; read-only source surface, caller and final policy gaps |

## Evidence interpretation and remaining gaps

The ION result is deliberately narrow. The static ELF evidence proves that
shipped ION libraries implement the node-opening and ioctl ABI boundary; it
does not identify which media/camera/graphics process called those exported
library functions, prove runtime execution, or establish an unprivileged
caller. The positive label therefore applies to the library-level provenance
join only.

For CMDQ, perfmgr, M4U, RPMB, IDME, diagnostics, and logger nodes, source
registration, config selection, policy allows, service/process/package names,
or library names were not treated as native callers. The remaining closure
work would require a bounded static scan of the exact shipped executable and
dependent-library call graph, plus final image node ownership/file-context
joins where the preserved artifacts do not already provide them. No runtime
access is needed or authorized for that gap.

## Existing-report reconciliation

This report extends, without changing, the conclusions of Phase 6SL
(`work/luna_worker_phase6sl_driver_callers_20260810.md`), Phase 6MZ,
6NA, 6MF/6MJ/6ML/6MN/6MO/6MP/6MS, Phase 6SG, and Phase 6QE. The key update
is that the earlier 6SL statement “no exact ION native caller” was too broad:
the Phase 5M static ION artifacts provide an exact shipped-library caller.
That does not close a top-level consumer identity or runtime route.

