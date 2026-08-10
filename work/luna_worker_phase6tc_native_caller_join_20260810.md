# Phase 6TC — exact native caller join

日期：2026-08-10（Asia/Taipei）  
範圍：GED、Vcodec、camera/ISP、sensor、thermal、USB/Type-C、PMIC，以及 Amazon proc/misc surfaces。這是 host-only static join；未執行 ELF、未開啟 device node、未執行 ioctl、proc/sysfs/debugfs write、ADB、Root 或 exploit。

## 判定規則與結論

本次只把下列證據同時閉合的 row 才能標為 `POSITIVE`：

1. exact-build GPL source/config 顯示 registration、fops、ioctl 或 proc/sysfs/debugfs operation；
2. preserved shipped inventory/policy/node metadata 指向同一 path；
3. exact shipped native ELF 的 strings 加上 symbol/relocation/call-site artifact，能把該 ELF/function 與 path-specific `open`/`read`/`write`/`ioctl`（或 proc/sysfs/debugfs equivalent）連起來。

本次 14 個 target rows 全部維持 `UNKNOWN`；沒有新的 `POSITIVE` exact shipped native caller。source/config/policy label、HAL/service/library name、或 query-only shell telemetry 都不算 caller。特別是 `libged*.so`、`libvcodec*.so`、camera/sensor HAL、thermal/USB service、PMIC library 與 `rpmb_svc` 的 inventory presence，均不足以閉合 native path。

## Row-level join

| ID | Surface / exact path | Existing source/config and shipped evidence | Native artifact check | Result | Exact gap |
|---|---|---|---|---|---|
| TC-01 | GED proc (`/proc/ged`) | `ged_main.c:321-326,392` has read/write/ioctl fops and proc creation; `CONFIG_MTK_GPU_SUPPORT`; prior file-context/debugfs labels | `phase5cs-native-inventory` lists `libged.so`, `libged_kpi.so`, `libged_sys.so`; no exact path string plus ELF call-site/relocation tuple. Prior `/proc/ged` shell query-only telemetry is not an ELF caller | UNKNOWN | shipped native proc open/read/write/ioctl caller |
| TC-02 | GED debugfs (`/sys/kernel/debug/ged/*`) | `ged_debugFS.c:114-173`; vendor file-contexts GED/debugfs labels | GED library names only; no exact debugfs path operation and call site | UNKNOWN | exact shipped ELF debugfs caller |
| TC-03 | Vcodec (`/dev/Vcodec`) | `videocodec_kernel_driver.c:1846,2972-2981,3112-3134`; `CONFIG_MTK_VIDEOCODEC_DRIVER=y`; vendor file-contexts `/dev/Vcodec` | `libvcodec_oal.so` and `libvcodec_utility.so` inventory presence only; no exact `/dev/Vcodec` string + open/ioctl call-site/relocation chain | UNKNOWN | exact shipped Vcodec node caller |
| TC-04 | Camera ISP nodes (`/dev/camera-*`, ISP family) | camera ISP source registration/ioctl paths; selected `CONFIG_MTK_CAMERA_ISP_*`; vendor file-contexts camera labels | no exact camera path string joined to a shipped ELF open/ioctl call site; HAL/library identity alone excluded | UNKNOWN | exact shipped camera node caller |
| TC-05 | Sensor misc nodes (`/dev/hwmsensor`, `/dev/gyroscope`, `/dev/barometer`, `m_*`) | sensor source/factory/ioctl paths; `CONFIG_MTK_SENSOR_SUPPORT=y` and selected sensor symbols; vendor labels | no exact sensor path + shipped ELF open/ioctl call-site/relocation tuple; sensor HAL presence excluded | UNKNOWN | exact shipped sensor node caller |
| TC-06 | Thermal proc (`/proc/mtkcooler`, `/proc/mtktz`) | `mtk_thermal_monitor.c:234-249,1089-1100,1615-1616`; thermal/writable-trip config selected | no exact proc path and native ELF read/write call site | UNKNOWN | exact shipped thermal proc caller |
| TC-07 | USB SSUSB sysfs (`mode`, `reg`, `cmode`) | `ssusb_sysfs.c:153,326,330,343-345`; USB MU3D/SIB config selected | no exact sysfs attribute path plus shipped ELF write call site; USB service/library names excluded | UNKNOWN | exact shipped USB sysfs writer |
| TC-08 | Type-C device/sysfs (`typec%u`) | `typec-ioctl.c:691-707,745-756` writable attrs and device creation; adjacent USB/PMIC config | no exact `/dev/typec*` or Type-C sysfs path joined to ELF open/write/ioctl call site | UNKNOWN | exact shipped Type-C caller |
| TC-09 | PMIC debugfs (`/sys/kernel/debug/mtk_pmic/dump_pmic_reg`) | `upmu_debugfs.c:127,165,203,323-351`; PMIC common/AUXADC/MT6358 config | no exact PMIC debugfs path + native ELF write/ioctl call site | UNKNOWN | exact shipped PMIC debugfs caller |
| TC-10 | PMIC device attrs (0664 sysfs attrs) | `upmu_debugfs.c:127,165,203`; selected PMIC config | no exact attribute path and shipped ELF read/write call site | UNKNOWN | exact shipped PMIC sysfs caller |
| TC-11 | Amazon IDME proc (`/proc/idme/*`) | `amzn_idme.c:315-344`; `CONFIG_AMZN_IDME=y`; preserved IDME proc/policy/init evidence; source path is read/seq-only | IDME HAL libraries in inventory but no exact `/proc/idme` string plus open/read call site or relocation chain | UNKNOWN | exact shipped IDME proc reader |
| TC-12 | Amazon lifecycle proc (`/proc/life_cycle_reason`) | `amzn_sign_of_life.c:255-265`; read-only mode 0444; lifecycle config selected | no exact proc reader ELF string/call site; kernel RTC setter is not a userspace caller | UNKNOWN | exact shipped lifecycle proc reader |
| TC-13 | Amazon metrics/vitals (`/dev/metrics`, `/dev/vitals`) | `amzn_logger.c:696-738`; read/poll/open/release-only misc fops; metrics config selected | no exact device path plus shipped ELF open/read/poll call site | UNKNOWN | exact shipped metrics/vitals reader |
| TC-14 | Amazon diagnostics (`/proc/amzn_drvs/*`) | `amzn_drv_test.c:784-841`; `CONFIG_AMZN_DRV_TEST` absent from trona and merged config; prior shipped snapshot lacks node | no shipped ELF caller; package/diagnostic HAL names are not path-specific evidence | UNKNOWN | shipped delivery and exact native caller |

## Evidence boundary

Inputs were the existing Phase 6SW/6SO outputs, the Phase 6SG/6SC caller-policy reconciliations, the preserved `phase5cs-native-inventory-20260804-01` inventories, and their exact shipped ELF strings/symbol/relocation/call-site artifacts as cited by those reports. The artifacts establish the negative native join above; they do not prove that no caller exists outside the bounded corpus. No runtime operation was used to fill any gap.

The prior 6SO ION library-level positive is out of scope and is not generalized to GED, Vcodec, camera/sensor, thermal, USB/Type-C, PMIC, or Amazon proc/misc. `UNKNOWN` here means the exact native caller join is not established, not that the kernel source surface or runtime node is proven absent.

