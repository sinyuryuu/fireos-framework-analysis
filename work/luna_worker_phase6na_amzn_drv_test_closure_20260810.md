# Phase 6NA — `amzn_drv_test.c` source closure

日期：2026-08-10

## Boundary

本報告是 **source-only** closure。只讀取
`firmware/extracted/PS7331-SOURCE-20250617/platform.tar` 的 tar member
串流；沒有解包或覆寫原始 archive，沒有執行 source binary、ADB、
`service call`、Binder transaction、ioctl、device node、Root、reboot、OTA
或 flash。本文不證明 runtime 載入、SELinux、UID/GID、實際 procfs 存在、
可達性、可利用性、漏洞或提權。

## Commands and inputs

執行的 host-only 命令：

```text
tar --list --file platform.tar | rg '(device/amazon/kernel/driver|trona_defconfig)'
tar --list --verbose --file platform.tar <member>
tar -xOf platform.tar <member> | sha256sum
tar -xOf platform.tar <member> | nl -ba | sed/rg ...
tar --list --file platform.tar | rg '(^|/)(Kconfig|Makefile|.*defconfig)$'
```

輸入 archive：

```text
firmware/extracted/PS7331-SOURCE-20250617/platform.tar
size: 1,617,756,160 bytes
SHA-256: 69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd
```

Selected member hashes:

| Member | Archive mode/size | SHA-256 |
|---|---|---|
| `device/amazon/kernel/driver/amzn_drv_test.c` | `-rw-r--r--`, 25,951 bytes | `6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e` |
| `device/amazon/kernel/driver/Kconfig` | `-rw-r--r--`, 1,788 bytes | `70ccd0fca0c20f90c867efe7e1d69167aa1e99954f277e56ee0b83d57b61da89` |
| `device/amazon/kernel/driver/Makefile` | `-rw-r--r--`, 1,141 bytes | `0f50ca76a8028be56db580f288aa81e231b0c9892b5517f4c5e0984c13fb861b` |
| `kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig` | `-rw-r--r--`, 14,743 bytes | `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac` |
| `device/amazon/kernel/driver/include/amzn_sign_of_life.h` | `-rw-r--r--`, 2,651 bytes | `8137f3c2a0a4f5b6cf8e2a04b223c1bb6674c9d7b8f9d6f2e7961fc00a4ab661` |
| `device/amazon/kernel/driver/include/amzn_idme.h` | `-rw-r--r--`, 882 bytes | `8a6f2373ac275bcd5ac00af71a398e15940f39137150fb6727d0a35504dd698c` |

## Kconfig and Makefile closure

`device/amazon/kernel/driver/Kconfig` defines the Amazon menu and options:

* `config AMZN` is the “Amazon Common Drivers” option at lines 1–7.
* The child options are inside `if AMZN` at line 9.
* `AMZN_IDME` is a bool depending on `PROC_FS` at lines 58–63.
* `AMZN_DRV_TEST` is a tristate “Amazon common BSP driver test module” at
  lines 65–70, with dependencies
  `AMZN_METRICS_LOG && AMZN_SIGN_OF_LIFE && AMZN_IDME` at line 67.

`device/amazon/kernel/driver/Makefile` provides the object mapping:

```text
lines 20–21: amzn_sign_of_life.o and amzn_sign_of_life_rtc_impl.o
lines 22–23: amzn_logger.o when metrics or Minerva metrics is y
line 25:     amzn_logger_test.o from CONFIG_AMZN_METRICS_LOG_TEST
line 26:     amzn_keycombo.o from CONFIG_AMZN_INPUT_KEYCOMBO
line 27:     amzn_idme.o from CONFIG_AMZN_IDME
line 28:     amzn_drv_test.o from CONFIG_AMZN_DRV_TEST
```

The Makefile also copies `include/amzn_*.h` into the kernel include tree at
line 18. The bounded archive path scan found no separate parent Kconfig or
Makefile member that explicitly includes `device/amazon/kernel/driver/Kconfig`
or this directory. Therefore menu inclusion into the complete kernel build is
**not closed by this archive-only pass**; the local driver Kconfig/Makefile
relationship and object conditional are confirmed.

`trona_defconfig` is useful configuration evidence: lines 523–530 contain
`CONFIG_AMZN=y`, `CONFIG_AMZN_SIGN_OF_LIFE=y`,
`CONFIG_AMZN_SIGN_OF_LIFE_RTC=y`, `CONFIG_AMZN_METRICS_LOG=y`,
`CONFIG_AMZN_MINERVA_METRICS_LOG=y`, `CONFIG_AMZN_IDME=y`,
`CONFIG_AMZN_INPUT_KEYCOMBO=y`, and `CONFIG_AMZN_POWEROFF_LOG=y`. There is no
`CONFIG_AMZN_DRV_TEST=y` or `CONFIG_AMZN_DRV_TEST=m` in the file. This means
the selected defconfig text does not select the test module; it does not prove
that another product config, generated config, build overlay, or shipped
module cannot select it.

## Names, modes, and proc object wiring

`amzn_drv_test.c` defines these literals at lines 32–35:

```text
AMZN_DRIVERS       "amzn_drvs"
AMZN_SIGN_OF_LIFE  "sign_of_life"
AMZN_IDME          "idme"
AMZN_LOGGER        "logger"
```

At initialization:

* `proc_mkdir(AMZN_DRIVERS, NULL)` creates the root concept at lines 792–799,
  so the intended path is `/proc/amzn_drvs`.
* `life_data->test_item` is set to `sign_of_life` at lines 807–809, then
  `proc_create_data(..., S_IRUGO|S_IWUSR, ..., &test_fops, life_data)` is
  called at lines 811–812.
* `idme_data->test_item` is set to `idme` at lines 821–823, then the same
  mode and `test_fops` are used at lines 825–826.
* `logger_data->test_item` is set to `logger` at lines 836–838, then the same
  mode and `test_fops` are used at lines 840–841.

Thus the source-intended child paths are:

```text
/proc/amzn_drvs/sign_of_life
/proc/amzn_drvs/idme
/proc/amzn_drvs/logger
```

The symbolic mode is exactly `S_IRUGO|S_IWUSR`; on the conventional Linux
permission constants this corresponds to owner read/write and group/other
read (`0644`). The source does not set an explicit owner or group on these
three entries. This is an observable source mode only, not effective runtime
permission or SELinux labeling.

The shared `test_fops` at lines 784–790 has `.open = proc_open`, `.read =
seq_read`, `.llseek = seq_lseek`, and `.write = proc_write`. The `proc_show`
read path at lines 720–740 displays `<test_item>=<test_index>` and shows help
when the index is zero. No device node is involved in this path.

## Write parsing and dispatch

`proc_write` at lines 747–781 is the complete first-layer write closure:

1. It obtains `drv_test_data` from `PDE_DATA(file_inode(file))` (line 750).
2. It rejects a null data pointer (754–757) and inputs of 64 bytes or more
   (759–760).
3. It copies the user buffer and NUL terminates it (762–765).
4. It parses exactly one decimal integer with `sscanf(input, "%d", ...)`
   (767–773). Non-numeric/multi-field input returns `-EINVAL`.
5. It calls `amzn_drv_test(pdata)` while holding the write semaphore (767–779)
   and returns the original byte count on success (781).

`amzn_drv_test` at lines 703–718 clears the result buffer, then dispatches by
the stored literal: `sign_of_life` → `sign_of_life_test`, `idme` → `idme_test`,
and `logger` → `logger_test`. The three independent comparisons are mutually
exclusive for the initialized names.

### Reachable index map (source-level)

All entries below are reachable from the corresponding proc write **if** the
module and proc entry exist and the write reaches `proc_write`. This table is
not runtime reachability evidence.

| Proc child | Accepted/handled indices | Source behavior |
|---|---|---|
| `sign_of_life` | `1`–`26` | `sign_of_life_test` switch at lines 236–404. `1` runs the combined interface test; `2`–`22` set/read boot, shutdown, thermal, or special reasons; `23` performs the RTC check-failed test path; `24` prints all reasons; `25` prints boot-up reasons; `26` clears lifecycle reasons. |
| `sign_of_life` | `0` | Does not enter the test switch when written; subsequent read shows help because `proc_show` treats index zero as help (732–733). |
| `sign_of_life` | any other integer | `default` at 397–403 records “no this test item” and then the common result handling runs. |
| `idme` | `1`–`6` | `idme_test` switch at lines 465–506: item lookup, board type, board revision, boot mode, device flags, and `board_has_wan`. |
| `idme` | `0` | Read-side help behavior via `proc_show`; no `case 0` in `idme_test`. |
| `idme` | any other integer | `default` at 501–505 records an invalid test item. |
| `logger` | `1`–`3` | `logger_test` switch at lines 612–640: metrics/vitals, metrics only, or vitals only. Results mention logcat commands at 618–634 but this report did not run them. |
| `logger` | `0` | Read-side help behavior; no `case 0` in `logger_test`. |
| `logger` | any other integer | `default` at 635–639 records an invalid test item. |

The source also declares `logger_loop` as a module parameter with mode `0644`
at lines 44–46. Its value controls the loop count in metrics/vitals tests at
lines 519–520 and 567–568; the parameter's runtime presence/value is not
established here.

## What this does and does not prove

**Confirmed source-only:** the literals, proc construction calls, symbolic
mode, shared write callback, integer parser, dispatch, and index switch bodies
listed above. The local Kconfig declares `AMZN_DRV_TEST` as a tristate with
three dependencies, and the Makefile maps it to `amzn_drv_test.o`.

**Strong configuration signal:** `trona_defconfig` enables the dependencies
and the parent `CONFIG_AMZN`, but does not select `CONFIG_AMZN_DRV_TEST`. This
is a useful negative result for that one defconfig, not proof of a final build
configuration.

**Unresolved:** parent Kconfig inclusion, generated `.config`, build overlays,
whether the test object is built as built-in/module, module load/init order,
actual `/proc/amzn_drvs` presence, owner/group/mode after procfs creation,
SELinux labels/domain permissions, caller UID, and any userspace path to
`proc_write`.

**Not inferred:** no runtime behavior, device-node access, ioctl behavior,
reboot/factory reset/OTA execution, vulnerability, exploitability, or
privilege escalation is claimed. The index names that mention factory reset,
OTA, and reboot are source test labels and code branches only.

