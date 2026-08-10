# Phase 6SW — Amazon/MediaTek kernel surface completeness

日期：2026-08-10（Asia/Taipei）  
範圍：PS7331 GPL source tar、`trona_defconfig`/保存的 `kernel.config`、extracted image policy/init/ueventd corpus，以及 exact shipped native ELF inventories。僅做 host-side static review；未開啟 device node，未執行 ioctl、proc/sysfs/debugfs write、ADB、payload、Root、exploit 或任何 runtime probe。

## 結論

本次補齊的是 6SO 之後的 Amazon/MediaTek kernel surface scope：Amazon driver、MediaTek `drivers/misc/mediatek`，以及 config-selected 的 input/power/USB/char-adjacent surfaces。結果見 companion CSV，共 18 rows；沒有新的 `POSITIVE` exact shipped native caller join。

判定採四段 join：

1. source registration/fops/ioctl/sysfs/proc/debugfs/device node；
2. selected config（優先 `trona_defconfig`，並對照保存的 merged `kernel.config`）；
3. extracted file-contexts/CIL/init/ueventd 或等價 shipped node evidence；
4. exact shipped native ELF 的 path-specific `open`/read/write/ioctl/proc/sysfs operation。

只具備 source、config、policy label、service/library name 的 row 保持 `UNKNOWN`。尤其 `libged.so`、`libvcodec*.so`、sensor/camera HAL 名稱與 `rpmb_svc` service presence 都不是 exact caller。

## Source/config completeness

`trona_defconfig` 明確選入 Amazon IDME、lifecycle、metrics/vitals、keycombo；MediaTek GPU/GED、camera ISP family、Vcodec、sensor family、thermal writable trips、USB MU3D/SSUSB、PMIC common/AUXADC、MEMCFG、M4U、CMDQ/ION 等。保存的 merged config 也顯示 MTK M4U、CMDQ CQDMA、camera ISP、GPU、Vcodec、sensor、USB 與 PMIC selections；`CONFIG_AMZN_DRV_TEST` 未在 trona 或保存 config 中選入，因此 driver-test proc 只能標為 source-only/conditional。

新 surface 的重要 source markers：

- `ged_main.c:321-326,392`：`read/write/unlocked_ioctl/compat_ioctl` 與 mode `0644` 的 GED proc entry；`ged_debugFS.c:114-173` 建立 GED debugfs。
- `upmu_debugfs.c:127,165,203,323-351`：PMIC 0664 device attrs 及 `mtk_pmic/dump_pmic_reg` writable debugfs。
- `mtk_memcfg.c:710-758`：`/proc/mtk_memcfg`，其中 engineering-gated entries 有 write handlers。
- `mtk_thermal_monitor.c:234-249,1089-1100,1615-1616`：`/proc/mtkcooler`、`/proc/mtktz` 與 writable thermal controls。
- `ssusb_sysfs.c:153,326,330,343-345`：USB mode/reg/cmode writable sysfs attrs。
- `typec-ioctl.c:691-707,745-756`：Type-C writable attrs 與 `typec%u` device creation。
- `videocodec_kernel_driver.c:1846,2972-2981,3112-3134,3518`：Vcodec ioctl fops、device nodes 與 debug sysfs。
- Amazon `amzn_idme.c:315-344`、`amzn_sign_of_life.c:255-265`、`amzn_logger.c:696-738`、`amzn_drv_test.c:784-841`：IDME read proc、lifecycle read-only proc、metrics/vitals read-only misc 與 conditional test proc。

## Policy/native join

Extracted `vendor_file_contexts` supplies labels for `/dev/Vcodec` (line 250)、camera ISP nodes (380–387, 404–405)、sensor nodes (350–352, 364–368, 389–394)、`/dev/audio_ipi` (353)、`/dev/M4U_device` (376)、RPMB nodes (430, 627, 650, 722) 與 GED/disp/PVR debugfs (470–471, 488, 587, 692)。這些 labels establish policy naming scope only；在 preserved extraction 中，許多 exact owner/mode/ueventd mapping 以及 domain-specific allow-to-caller join 仍缺。

Native inventories (`phase5cs-native-inventory-20260804-01`) list `libged.so`, `libged_kpi.so`, `libged_sys.so`, `libvcodec_oal.so` and `libvcodec_utility.so`; identity inventory lists `rpmb_svc` running. The bounded native strings/symbol inventories contain no exact path-specific caller tuple for the new GED, PMIC, thermal, USB/Type-C, Vcodec, camera, sensor, Amazon logger/lifecycle, or RPMB surfaces. Therefore no row is promoted to a shipped native caller result.

## Existing 6SO exclusions

ION/CMDQ/perfmgr/M4U/RPMB/IDME/logger conclusions are referenced only. They are not re-scanned here. In particular, 6SO's narrow positive remains the shipped ION library-level caller; it does not imply a top-level process caller. The CSV includes M4U and RPMB as prior-result references solely to preserve scope completeness, not to repeat their analysis.

## Provenance and limits

- GPL platform tar: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar`, SHA-256 `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`.
- `trona_defconfig`, SHA-256 `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac`.
- merged `kernel.config`, SHA-256 `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04`.
- extracted `vendor_file_contexts`, SHA-256 `db5cd91b8d25170ad27809ace8cdbbd2a3f838ec72e2598a4f6b5a44953d322e`；`vendor_sepolicy.cil`, SHA-256 `82430dbe87b8a5f653110b635289489b99e82bdbe7bdc7a2e1ee5564e674e035`.

This is a completeness/evidence-boundary result, not a claim that any node exists at runtime or that any ordinary app can reach a write/ioctl path. Safe follow-up remains host-only: obtain exact final ueventd/file-context/TE joins and path-specific native callsites if the corresponding artifacts are supplied.
