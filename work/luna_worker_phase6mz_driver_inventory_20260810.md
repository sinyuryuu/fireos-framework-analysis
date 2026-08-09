# Phase 6MZ — PS7331 GPL driver/procfs/sysfs inventory

日期：2026-08-10

## Scope and method

本報告只盤點本機 archive/source；沒有連接裝置，也沒有執行 source
binary、ADB、`service call`、Binder transaction、ioctl、Root、reboot、OTA
或 flash。原始 tar 未解包、未覆寫。所有 source 命中均為 archive member
的離線文字串流讀取；行號是該 member 內的 `nl -ba` 行號。這些結果是
靜態存在性與程式碼意圖證據，不是裝置上實際掛載、SELinux policy、runtime
UID 或可達性的證明。

## Inputs and reproducibility

實際執行的命令包括：

```text
stat -f '%z %N' firmware/extracted/PS7331-SOURCE-20250617/{fireos,platform}.tar
sha256sum firmware/extracted/PS7331-SOURCE-20250617/{fireos,platform}.tar
tar --list --file <archive> | head -40
tar --list --file <archive> | rg -i '(amazon|mediatek|mtk|procfs|sysfs|debugfs|/dev/|ioctl|engineering|factory|diag|engmode|kft|fos)'
tar -xOf <archive> <member> | nl -ba | rg -i '<marker-regex>'
tar --list --verbose --file <archive> <selected-member>
tar -xOf <archive> <selected-member> | sha256sum
```

| Input | Size | SHA-256 | Status |
|---|---:|---|---|
| `firmware/extracted/PS7331-SOURCE-20250617/fireos.tar` | 688,250,880 bytes | `bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369` | Confirmed, readable tar |
| `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | 1,617,756,160 bytes | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` | Confirmed, readable tar |

The archives were suitable for the requested scan: `tar --list` completed,
targeted member streams could be read, and no extraction directory was needed.

## Amazon driver inventory (`platform.tar`)

The device-specific Amazon path is:

```text
device/amazon/kernel/driver/
```

The following members were present. The mode shown is the archive member mode,
not a claim about the installed kernel object or runtime proc/device mode.

| Member | Archive mode/bytes | Member SHA-256 | Static markers and lines |
|---|---|---|---|
| `device/amazon/kernel/driver/amzn_idme.c` | `-rw-r--r--`, 8,101 | `ab6484ae7a694412ec4eeabb67133ddd0c0af221076b6d989c8ab1fe7c84e61e` | `/idme/*` DT paths at 23–30; proc root at 315–316; permission read at 334; write bits removed at 337–338; restricted `0400` and owner `MAC_SEC_OWNER:root` at 340–347; `proc_create_data` at 343–344. |
| `device/amazon/kernel/driver/amzn_drv_test.c` | `-rw-r--r--`, 25,951 | `6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e` | root `/proc/amzn_drv` at 792–799; child entries created with `S_IRUGO|S_IWUSR` at 811–812, 825–826, 840–841; write handler is present in `test_fops` at 784–790. Help text describes `echo [index] > idme/logger` at 681–682 and factory-reset/OTA special-mode test labels at 670–671. |
| `device/amazon/kernel/driver/amzn_logger.c` | `-rw-r--r--`, 21,955 | `9293b2f75e8e7760f961d5849b3fe3e666e8e2df0b2906b6fcdf4b2190d7afbd` | `amazon_logger_fops` has read/poll/open/release and no write at 696–702; dynamic misc device name and `misc_register` at 704–738; docs identify `/dev/metrics` and `/dev/vitals` and state read-only/no write at `Documentation/amazon_logger.txt:104–109`. |
| `device/amazon/kernel/driver/amzn_sign_of_life.c` | `-rw-r--r--`, 12,306 | `87e455617e0960658bade537a316c5168a47048db1f2e72922b3e38129449419` | read-only `/proc/life_cycle_reason` with mode `0444` at 262–265; exported setters for lifecycle reasons at 307–323, 332–350, and special mode beginning 353; reboot notifier registration at 429–435. |
| `device/amazon/kernel/driver/Documentation/idme.txt` | `-rw-r--r--`, 1,726 | `636b166de98f9ef16db2e04fd7683107b297d5cf030cf441540fbf1abd35f949` | Documents `/proc/idme` and example fields at 39–45. |
| `device/amazon/kernel/driver/Documentation/amazon_logger.txt` | `-rw-r--r--`, 4,003 | `e73ccdae5f86c62dfc7212e5135c62e365e4013da7d1064c8e3a4957b34118cf` | Documents `/dev/metrics` and `/dev/vitals`, read/poll/select and read-only behavior at 104–109. |
| `device/amazon/kernel/driver/Documentation/sign_of_life.txt` | `-rw-r--r--`, 2,115 | `198f04e2fe6e119e4898e00435e03ee467b7ec1287ec939a1e9986a8a711e705` | Documents `/proc/life_cycle_reason` at 6–11 and OTA/factory-reset special-mode concepts at 37–47. |

### Amazon conclusions and limits

**Confirmed:** source contains an IDME procfs producer, a read-only lifecycle
reason proc entry, Amazon logger misc devices, and a test proc subtree with a
write callback. The IDME implementation explicitly strips write bits from DT
permissions and restricts the MAC security key to `0400` with a designated
owner. The logger file operations shown here do not expose a write callback.

**Strong static marker:** `amzn_drv_test.c` contains engineering/factory-like
test controls and labels for factory-reset and OTA special modes. This proves
test/control code is in the source; it does not prove that a normal user can
reach it, that the module is built/loaded, or that a device node is exposed.

**Unresolved:** exact `AMZN_DRIVERS` string value, compiled Kconfig selection,
init/module load path, installed SELinux labels, runtime owner/group/mode,
and any userspace caller. No device-side permission or reachability check was
performed.

## MediaTek inventory (`platform.tar`)

The archive contains the MT8183 kernel tree at
`kernel/mediatek/mt8183/4.4/` and vendor modules under
`vendor/mediatek/kernel_modules/`. The path search found broad upstream and
SoC code; only device-specific examples and their static permissions are
summarized below.

| Member | Archive mode/bytes | Member SHA-256 | Static markers and lines |
|---|---|---|---|
| `kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/performance/perf_ioctl/perf_ioctl.c` | `-rw-r--r--`, 6,002 | `df846d7463d14af07fa98bb0a26d389c1a5e41a46b58763327c9d47a2aa3ff09` | `.unlocked_ioctl` and `.compat_ioctl` at 200–201; proc entry `perfmgr/perf_ioctl` mode `0664` at 231. This is an ioctl/proc marker, not evidence of a caller or exploitability. |
| `kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/pmic/common/upmu_debugfs.c` | `-rw-r--r--`, 9,452 | `db8dfc551225586a717af6cc96057b8d810548cf123bd555cfb5d5698b5ec092` | debugfs directory `mtk_pmic` at 323; `dump_pmic_reg` with `S_IRUGO|S_IWUSR` at 330; `pmic_dump_exception` and `pmic_dbg_level` read-only `S_IRUGO` at 332–334; device attributes at 348–351. |
| `kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/gpu/ged/src/ged_main.c` | `-rw-r--r--`, 14,953 | `95671972e22b12d0f6301c28750ebc28e371e02a75610ff62a94a90953fa30c5` | GED `.unlocked_ioctl`/`.compat_ioctl` at 342–344; proc entry with mode `0644` at 411. |
| `kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/gpu/ged/src/ged_debugFS.c` | `-rw-r--r--`, 4,972 | `7c6530b4ecfe6c142d1fbfac7c26c9e242c511216cd295b9836958fdebea88a5` | `debugfs_create_file` at 114, directory creation at 152 and 173. |
| `kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/ext_disp/mt8183/extd_factory.c` | archive source member; content hash not separately required for this inventory | not computed | factory functions `hdmi_factory_mode_init` at 59, `hdmi_factory_mode_test` at 222, and factory callbacks at 309–345. |
| `kernel/mediatek/mt8183/4.4/drivers/misc/mediatek/sspm/sspm_sysfs.c` and callers | archive source members | not computed | SSPM sysfs creation callers include `sspm_plt.c:139`, `sspm_timesync.c:209`, `sspm_excep.c:121–126`, and `sspm_logger_impl.c:320–326`. Exact runtime attribute modes and write callbacks remain unresolved here. |

Additional path-only hits include MediaTek sensor factory files, PMIC debugfs,
GPU GED debugfs, USB PHY debugfs, and HPS procfs. Generic kernel `ioctl`,
`sysfs`, `debugfs`, and `procfs` filenames were not treated as Amazon or
MediaTek-specific evidence unless their path was under the MT8183/MediaTek or
Amazon trees.

## `fireos.tar` result

`fireos.tar` was readable and was scanned with `tar --list`. The bounded path
search found no `amzn`, `idme`, `firelauncher`, or Amazon driver path. It did
contain generic `kernel/goldfish` procfs/sysfs/debugfs/ioctl source paths and
generic external tools (including `e2fsprogs/debugfs`). Those are classified
**Confirmed generic source markers**, not PS7331 Amazon/MediaTek device-driver
markers. A path-name scan cannot establish compilation or runtime exposure.

## Evidence classification

* **Confirmed:** both tar archives exist, hashes match the listed local files,
  Amazon/MediaTek source members and the cited marker lines exist in the
  archive, and the source-declared modes/registration calls are as recorded.
* **Strong static marker:** Amazon test controls, Amazon proc/misc interfaces,
  and MediaTek ioctl/debugfs/sysfs/factory code have explicit source support.
* **Unproven:** actual `/proc`, `/sys`, `/sys/kernel/debug`, or `/dev` nodes on
  the target; effective runtime permissions/SELinux; build/config inclusion;
  module loading; userspace caller identity; Binder/IPC reachability; and any
  security impact.
* **Rejected/not inferred:** no vulnerability, privilege escalation, root
  path, or normal-user access claim is made from these static markers.

## Smallest safe follow-up

The smallest non-device follow-up is a source-only closure of the Amazon test
proc path: resolve `AMZN_DRIVERS` and the three `proc_create_data` names,
follow `proc_write` to each test dispatch, and map Kconfig/Makefile inclusion.
This would clarify names and build reachability without reading or writing a
device node. A separate bounded pass can then map the MediaTek `0664`/`0644`
proc entries and debugfs writers to their Kconfig/module inclusion. Neither
pass should execute the source or invoke ioctl/device operations.

