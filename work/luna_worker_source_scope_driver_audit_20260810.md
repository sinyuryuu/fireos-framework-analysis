# PS7331 source-scope / driver audit (host-only)

日期：2026-08-10
範圍：只讀本機已解包 PS7331 source、Image 與既有 artifacts。未執行
ADB/device/Binder/ioctl/root/OTA/updater，未寫入 device、partition 或其他
檔案；沒有 exploit 結論。

## 結論先行

1. **`system/core/init`：source scope 中不存在。** `platform/system/core/`
   只含 `libcutils/`、`logwrapper/` 等；`platform.tar` 的 `system/core`
   成員也沒有 `system/core/init`、`selinux.cpp` 或 Android userspace policy
   loader。可見的 `init/` 是 Linux kernel init，不是 Android `/init`。
2. **Amazon driver：有 source/build 接線，但不是 `drivers/amazon/`。**
   實際 Amazon paths 是 `device/amazon/kernel/driver/` 與
   `kernel/.../drivers/staging/amazon/`。`drivers/staging/Kconfig:117-120`
   引入 Amazon Kconfig，`drivers/staging/Makefile:52-53` 以 `CONFIG_AMAZON`
   或 `CONFIG_AMZN` 接入；這是 build reachability 的靜態證據，不是已載入
   或可由 app/shell 使用的證據。
3. **`amzn_drv_test` 是工程/測試 source surface，對 trona config 有強負面訊號。**
   `Kconfig:65-68` 宣告且 default n，`Makefile:28` 才會編入；
   `trona_defconfig` 的 Amazon 依賴在 `523-530`，但沒有
   `CONFIG_AMZN_DRV_TEST=y/m`。既有 Image marker audit 在官方 Image
   只見 3/9 markers，六個專屬 test markers（含 `amzn_drvs`）缺失。
4. **MediaTek engineering/debug/factory surface 確實存在，部分與官方
   Image 有 literal 對應。** `mtk_auxadc.c` 有 ioctl、factory-mode 註解、
   大量 sysfs attributes 與可寫 proc debug entry；官方 Image 也保留
   `AUXADC`、`store_AUXADC_register`、`AUXADC_read_channel` 等 strings。
   這只證 source/image marker 對應，不證明 node mode、SELinux 或 caller
   可達性。

## Provenance / hash manifest

| 輸入 | SHA-256 | 用途 | 信心 |
|---|---|---|---|
| `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` | 外層官方 source archive；既有 EOF audit：35 members、完整到 EOF | Confirmed |
| `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` | GPL kernel/Amazon source scope | Confirmed |
| `firmware/extracted/PS7331/boot_unpacked/Image` | `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d` | 保存的官方 PS7331 boot Image | Confirmed |
| `kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig` | `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac` | build-selected config member | Confirmed |

Key member hashes:

```text
device/amazon/kernel/driver/amzn_drv_test.c                         6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e
device/amazon/kernel/driver/amzn_idme.c                             ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e
device/amazon/kernel/driver/amzn_sign_of_life.c                     87e455617e0960658bade537a316c5168a47048db1f2e72922b3e38129449419
device/amazon/kernel/driver/amzn_logger.c                           9293b2f75e8e7760f961d5849b3fe3e666e8e2df0b2906b6fcdf4b2190d7afbd
kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/auxadc/mtk_auxadc.c 5ffbce942417fc6aca773d90e4c6935f508087f9a80d96138a7ecc30561ed327
kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/boot/mtk_boot_common.c 2bdb2da132c31cb867a80a7b2c0e50724a11da75825c3e8a8509761de3396fe4
kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/mem/mtk_memcfg.c fb1f13f8a15c79554461235a6a6487f4cf36e5e05e4139f3b93c97445b59df08
kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/ext_disp/mt8183/extd_factory.c de7d7b633bc5488c50b582f2cbd6db6ee030b3c364dd6142a03305390930989
kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/pmic/common/upmu_debugfs.c db8dfc551225586a717af6cc96057b8d810548cf123bd555cfb5d5698b5ec092
```

## Source/build wiring and actual Image correspondence

### Amazon

| Evidence | Location | Interpretation |
|---|---|---|
| Amazon Kconfig inclusion | `platform/kernel/mediatek/mt8183/4.4/drivers/staging/Kconfig:117-120` | `drivers/staging/amazon/Kconfig` and `device/amazon/kernel/driver/Kconfig` are in the source build graph | Strong static |
| Amazon Makefile inclusion | `.../drivers/staging/Makefile:52-53` | `CONFIG_AMAZON`/`CONFIG_AMZN` selects Amazon directories | Strong static |
| IDME proc producer | `device/amazon/kernel/driver/amzn_idme.c:316,343` | `/proc/idme` root/children are source-defined; permissions are further processed in nearby code | Confirmed source-only |
| lifecycle proc producer | `amzn_sign_of_life.c:264` | `/proc/life_cycle_reason`, source mode 0444 | Confirmed source-only |
| test proc producer/write | `amzn_drv_test.c:762,797,811,825,840,866` | input copy, `/proc/amzn_drv`, three writable test children, module init | Confirmed source-only |
| test option | `device/amazon/kernel/driver/Kconfig:65-68`; `Makefile:28` | tristate, default n, depends on metrics/sign-of-life/IDME | Confirmed |
| selected config | `trona_defconfig:523-530` | dependencies are enabled; test option itself is absent | Strong negative for named defconfig |
| official Image markers | `artifacts/phase6nd-amzn-drv-test-image-marker-20260810-01/phase6nd-image-marker-audit.md:3-9` | 3/9 markers observed; six test-specific markers absent | Strong bounded negative; not module/runtime proof |

### MediaTek / factory / debug

| Evidence | Location | PS7331 Image/source relation |
|---|---|---|
| boot mode proc/device path | `drivers/misc/mediatek/boot/mtk_boot_common.c:191-212,262-268,321-349` | source defines boot-mode sysfs/device and `/proc/boot_mode`; Image marker search found `boot_mode`-related kernel strings in the saved Image | Source + marker correspondence; runtime node unknown |
| AUXADC ioctl | `drivers/misc/mediatek/auxadc/mtk_auxadc.c:553-667` | `.unlocked_ioctl`/`.compat_ioctl` and source ioctl diagnostics | Source surface; no host-side invocation |
| AUXADC factory/debug | `mtk_auxadc.c:1384,1515-1651,1718-1719,1973` | explicit factory comment, many device attributes, writable `dump_auxadc_status`, module init | Source surface; Image contains `AUXADC` and `store_AUXADC_*` literals |
| MTK memory proc/debug | `drivers/misc/mediatek/mem/mtk_memcfg.c:671-771` | `CONFIG_MTK_ENG_BUILD` gates some entries; `/proc/mtk_memcfg`, writable trigger entries, module init | Source-only; final config/image registration not closed |
| PMIC debugfs/sysfs | `drivers/misc/mediatek/pmic/common/upmu_debugfs.c:323-351` | `mtk_pmic`, writable `dump_pmic_reg`, read-only entries and PMIC attrs | Source-only; debugfs policy unknown |
| HDMI factory code | `drivers/misc/mediatek/ext_disp/mt8183/extd_factory.c:59-70,222-327,332-352` | factory callbacks exist behind display driver integration | Historical/product BSP code unless exact caller/config is shown; no Image marker used as positive proof |
| broad driver controls | `artifacts/phase6me-driver-control-edges-20260810-01/summary.json` | 1,671 files; 1,726 ioctl markers; 703 proc/sysfs/debugfs markers; no framework/launcher sinks; runtime policy explicitly not derived | Strong inventory, not reachability |

## init / policy loader boundary

* `firmware/extracted/PS7331-SOURCE-20250617/platform/system/core/` contains
  `libcutils` and `logwrapper`, but no `init/` directory. A direct filesystem
  check for `platform/system/core/init` returns absent.
* `platform.tar` contains kernel `init/` (`kernel/.../init/main.c`,
  `do_mounts*.c`, `initramfs.c`) and kernel SELinux implementation, but no
  Android userspace `system/core/init` or policy loader. This distinction is
  important: kernel `init/main.c` is not the Android `/init` binary.
* The only conspicuous `install_policy.sh` is
  `kernel/mediatek/mt8183/4.4_emc/scripts/selinux/install_policy.sh:1-68`.
  It is a host/build-side legacy script using `id`, `checkpolicy`, `setfiles`
  and `/etc/selinux/dummy`; it is not evidence of a Fire OS boot-time loader,
  and it was not run.
* Existing image extraction has selected framework files and partition images,
  but no checked-in extracted `/init`, `file_contexts`, `property_contexts`,
  `service_contexts`, or `.rc` set in the selected source artifact. Therefore
  init import order, module load path, effective SELinux labels and runtime
  Unix modes remain **Unknown**, not inferred from source modes.

## Historical/dead-code versus PS7331-corresponding

| Classification | Items | Basis |
|---|---|---|
| PS7331 source + build-corresponding | MT8183 `trona_defconfig`, Amazon Kconfig/Makefile chain, MTK AUXADC/boot/mem/PMIC sources | Same `platform.tar`, selected `mt8183/4.4` root and config hash | High for source/config identity |
| PS7331 source + bounded Image marker | AUXADC strings; `amzn_drv_test` negative marker audit; official Image hash above | Direct raw-string scan of saved Image; marker absence remains bounded | Medium/High for marker only |
| source-visible but not proven shipped | `amzn_drv_test`, writable test proc children, `CONFIG_MTK_ENG_BUILD`-gated mem entries, HDMI factory callbacks, PMIC debugfs writers | No generated final `.config`, module list, init loader, SELinux label or runtime node evidence | High that runtime is unresolved |
| historical/legacy build-side | `4.4_emc/scripts/selinux/install_policy.sh` and its dummy `/etc/selinux` install flow | Host-side script, not Android `system/core/init`; not executed | High |
| generic/dead for this requested route | absent `drivers/amazon/`; absent source `system/core/init`; generic kernel init sources | Exact path/member absence in bounded source scope | High |

## Reachability statement

The strongest defensible chain is:

```text
source registration / Kconfig
        -> possible built-in driver or module (config/module packaging unresolved)
        -> possible proc/sysfs/debugfs/device node (init + SELinux + mode unresolved)
        -> caller permission and runtime reachability (not established)
```

No source marker here is promoted to an exploit, root route, Binder route,
launcher/package-manager sink, or privilege transition. Existing driver-control
artifacts explicitly report `runtime_reachability: not-derived-from-source` and
`framework_sink/launcher_sink: none-observed`; this audit preserves that boundary.

## Reproducibility references

* `artifacts/phase6me-driver-control-edges-20260810-01/summary.json`
* `artifacts/phase6nb-amzn-drv-test-source-closure-20260810-04/phase6nb-amzn-drv-test-source-closure.md`
* `artifacts/phase6nd-amzn-drv-test-image-marker-20260810-01/phase6nd-image-marker-audit.md`
* `artifacts/phase6mi-source-tar-eof-20260810-03/source-tar-summary.csv`
* `work/luna_worker_phase6mz_driver_inventory_20260810.md` (prior inventory; this report adds init/policy-loader and source-to-Image boundary evidence)
