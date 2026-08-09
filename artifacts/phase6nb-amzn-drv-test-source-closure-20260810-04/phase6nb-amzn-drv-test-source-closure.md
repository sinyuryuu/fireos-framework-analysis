# Phase 6NB — `amzn_drv_test.c` host-only source closure

Date: 2026-08-10
Classification: host-only static evidence; no device mutation

## Scope

This report reads four members from the Amazon GPL `platform.tar` stream. It
does not extract the archive, execute source code, access `/proc` on the
tablet, call Binder or ioctl, install an APK, reboot, modify a partition, or
attempt root. A source test label mentioning OTA, factory reset, or reboot is
not treated as proof that the corresponding path exists or is reachable on the
retail build.

Archive: `firmware/extracted/PS7331-SOURCE-20250617/platform.tar`
Archive SHA-256: `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd`
Driver source lines: `870`

## Selected member hashes

| Member | SHA-256 |
|---|---|
| `device/amazon/kernel/driver/amzn_drv_test.c` | `6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e` |
| `device/amazon/kernel/driver/Kconfig` | `70ccd0fca0c20f90c867efe7e1d69167aa1e99954f277e56ee0b83d57b61da89` |
| `device/amazon/kernel/driver/Makefile` | `0f50ca76a8028be56db580f288aa81e231b0c9892b5517f4c5e0984c13fb861b` |
| `kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig` | `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac` |

## Findings

### Confirmed source facts

* `Kconfig` declares `AMZN_DRV_TEST` (line(s) 65) with dependencies
  on the Amazon metrics, sign-of-life, and IDME options.
* `Makefile` maps `CONFIG_AMZN_DRV_TEST` to `amzn_drv_test.o`
  (line(s) 28).
* The driver names the proc root `amzn_drvs`, creates the three intended child
  names `sign_of_life`, `idme`, and `logger`, and uses the shared `test_fops`
  with a write callback. The source requests `S_IRUGO|S_IWUSR` for those
  entries.
* The write path bounds the input, copies it, parses a decimal index, and
  dispatches to the corresponding test routine. The exact branch bodies and
  line references are in the evidence CSV.

### Strong negative configuration signal

`trona_defconfig` contains the Amazon parent/dependency selections:

```text
CONFIG_AMZN_THERMAL_VIRTUAL_SENSOR=y
CONFIG_AMZN=y
CONFIG_AMZN_SIGN_OF_LIFE=y
CONFIG_AMZN_SIGN_OF_LIFE_RTC=y
CONFIG_AMZN_METRICS_LOG=y
CONFIG_AMZN_MINERVA_METRICS_LOG=y
CONFIG_AMZN_IDME=y
CONFIG_AMZN_INPUT_KEYCOMBO=y
CONFIG_AMZN_POWEROFF_LOG=y
```

It has no `CONFIG_AMZN_DRV_TEST=y` or `CONFIG_AMZN_DRV_TEST=m` line
(NOT_FOUND). This is evidence about that defconfig only; it does not close
generated `.config` files, product overlays, module packaging, or another
product configuration.

### Not established

The archive-only evidence does not establish Kconfig parent inclusion in the
final build, generated configuration, whether the object is built or loaded,
whether `/proc/amzn_drvs` exists on the device, effective ownership/mode,
SELinux labeling, caller permissions, a userspace caller, vulnerability,
exploitability, or privilege escalation.

## Reproduction

```text
python3 -B tools/scripts/audit_phase6nb_amzn_drv_test_source.py \
  --archive firmware/extracted/PS7331-SOURCE-20250617/platform.tar \
  --output artifacts/phase6nb-amzn-drv-test-source-closure-YYYYMMDD-NN
sha256sum -c artifacts/phase6nb-amzn-drv-test-source-closure-YYYYMMDD-NN/sha256sums.txt
```

## Evidence classification

| Evidence | Meaning | Confidence |
|---|---|---|
| 6NB-S01..S11 | Source member content and line-local wiring | Confirmed |
| `trona_defconfig` omission | Negative evidence for this named defconfig | Strong evidence |
| Final image/procfs/SELinux/runtime behavior | Not present in this phase | Unknown |
