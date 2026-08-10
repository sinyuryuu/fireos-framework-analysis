# Phase 6TX — `amzn_drv_test` exact host-only closure

日期：2026-08-10

## Scope and disposition

本輪只做 host-only static closure：GPL source、PS7331 boot `Image`/manifest、
以及 Phase 6N/6NP/6NB/6ND artifacts 的 exact config/object/image/file-context/
SELinux/init/uevent 對照。沒有執行裝置命令、binary、module load、proc/sysfs/
debugfs write、device-node open、ioctl、Binder、root、exploit、reboot 或任何
mutation。

結論：`amzn_drv_test` 的 source registration 是 **LOCAL_ONLY**；在可核對的
PS7331 final config 與 built-in `Image` 中沒有 shipped proof，且 exact module
payload、`/proc/amzn_drvs` runtime nodes、file modes/labels、SELinux caller
allow、init/uevent load path 均未閉合，故保留 **UNKNOWN**。已確認的缺失只在
對應 bounded corpus 內標為 **ABSENT**，不外推到未提供的 product payload。

## Exact inputs and hashes

| Input | SHA-256 | Role |
|---|---|---|
| `firmware/extracted/PS7331-SOURCE-20250617/platform.tar` | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` | GPL source container |
| `device/amazon/kernel/driver/amzn_drv_test.c` tar member | `6c2309f996cacafaab35cce3935bcb725a5259211751af89df88d3732797029e` | source |
| `device/amazon/kernel/driver/Kconfig` tar member | `70ccd0fca0c20f90c867efe7e1d69167aa1e99954f277e56ee0b83d57b61da89` | config declaration |
| `device/amazon/kernel/driver/Makefile` tar member | `0f50ca76a8028be56db580f288aa81e231b0c9892b5517f4c5e0984c13fb861b` | object mapping |
| `kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig` tar member | `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac` | named defconfig |
| `firmware/extracted/PS7331/boot.img` | `cf12e5619d635ecf7927784a4ed15a254a96c1642d1db9e4ca6734b192d6fa1b` | official boot input |
| `firmware/extracted/PS7331/boot_unpacked/Image` | `10638df8d43c83e0799bfe071ef29a8069ad909b320536cff6b58ee5e1efea7d` | kernel Image |
| `firmware/extracted/PS7331/selected/extraction-manifest.tsv` | `b098f85287a729d03cfac1ac6f767a3ba6a15ce8c65d7f9e581cbbed75448a74` | selected manifest |
| `firmware/extracted/PS7331/compiled-02/extraction-manifest.tsv` | `7da7040b4c7454084d8c30452edc05d4c68ce3813fe20700d4016036e4097716` | compiled manifest |
| `artifacts/phase5/ps7331-ikconfig-20260804-01/kernel.config` | `eefb8db484f65e196a7bb401ae0165f434f08b13041aef6762917e284d013d04` | extracted final config |

## Closure matrix

### Source, CONFIG and object inclusion

`Kconfig:65-70` declares tristate `AMZN_DRV_TEST`, dependent on
`AMZN_METRICS_LOG && AMZN_SIGN_OF_LIFE && AMZN_IDME`. `Makefile:28` maps
`obj-$(CONFIG_AMZN_DRV_TEST)` to `amzn_drv_test.o`. This proves only a local
conditional build edge.

The named `trona_defconfig` has the parent/dependency options enabled but no
`CONFIG_AMZN_DRV_TEST=y` or `=m` line (`NOT_FOUND`). The extracted PS7331 final
config is stronger for the selected build: `CONFIG_MODULES=y` at line 250, but
`# CONFIG_AMZN_DRV_TEST is not set` at line 3584. Therefore built-in inclusion
is negatively evidenced for that exact config; generic module support does not
select or ship this object. No `.ko`, `modules.dep`, `modules.load`,
`vendor_dlkm`, `odm`, or `amzn_drv_test` module payload was found in the audited
selected/compiled extraction corpus. The module-discipline status remains
**UNKNOWN** outside that corpus, while the searched corpus entry is **ABSENT**.

### Image and manifest

The official `Image` marker audit found zero occurrences for the unique driver
markers `amzn_drvs`, `logger_loop`, `sign_of_life_test`, `idme_test`,
`logger_test`, and `no this test item`. Generic strings `sign_of_life`, `idme`,
and `logger` do occur, but are explicitly excluded because they are not
driver-specific. This is strong bounded negative evidence against built-in
`amzn_drv_test`; it is not proof against an unenumerated loadable module.

The selected and compiled PS7331 manifests contain no matching
`amzn_drv_test`/`.ko` payload in the audited file lists. This closes only the
provided manifest corpus, not an unspecified external packaging source.

### Intended `/proc/amzn_drvs` nodes and source modes

Source literals at `amzn_drv_test.c:32-35` name `amzn_drvs`, `sign_of_life`,
`idme`, and `logger`. `proc_mkdir` is at lines `797-799`; child creation is at
`811-812`, `825-826`, and `840-841`; the shared fops at `784-790` includes
`.write = proc_write`. The source-requested child mode is exactly
`S_IRUGO|S_IWUSR`, conventionally `0644`, with no explicit source owner/group.

These are **LOCAL_ONLY** intended objects and source-requested modes. Phase 6N
read-only metadata confirms other Amazon proc surfaces (`/proc/idme/*`), not
`/proc/amzn_drvs`; no runtime existence, effective mode/owner, or label is
claimed. No proc path was written or opened.

### File-context, SELinux, init and uevent

The bounded extracted policy/file-context corpus has no exact
`amzn_drvs`/`proc_amzn_drvs` mapping or driver-specific allow rule that can be
joined to a shipped object. Thus exact file label, domain permission, and
caller reachability are **UNKNOWN**. Existing `proc_idme` labels and Phase 6N
metadata must not be transferred to this separate test proc tree.

No matching init module-load action, `modules.load` entry, uevent rule, or
driver-specific startup declaration was found in the audited PS7331 manifests.
The source `module_init` registration is **LOCAL_ONLY** and is not an init/
uevent shipping proof. A missing declaration in this corpus is recorded as
**ABSENT** only for that corpus; external init/uevent inputs remain **UNKNOWN**.

## Final status

| Claim | Status | Exact boundary |
|---|---|---|
| Source Kconfig option and dependency | Confirmed / LOCAL_ONLY | `Kconfig:65-70` |
| Source object mapping | Confirmed / LOCAL_ONLY | `Makefile:28` |
| `trona_defconfig` selects test | ABSENT | named defconfig, no `y/m` line |
| PS7331 final config selects test | ABSENT | `kernel.config:3584` |
| Built-in `Image` contains driver | Strong negative; not shipped proof | unique markers all zero |
| Loadable module shipped | UNKNOWN; matching audited payload ABSENT | no `.ko`/module manifest in corpus |
| `/proc/amzn_drvs` nodes exist | UNKNOWN | source-only intended paths |
| Effective mode/owner/SELinux label | UNKNOWN | source requests 0644 only |
| init/uevent load path | UNKNOWN; matching audited declaration ABSENT | no exact declaration in corpus |
| Caller/effect | UNKNOWN | no caller or effect inferred |

The safe stop point is therefore: **no evidence that `amzn_drv_test` was
shipped in the PS7331 built-in kernel or audited module corpus; no evidence of
runtime `/proc/amzn_drvs` nodes; source registration is not shipped caller or
effect evidence.**

## Evidence references

- Phase 6NB source artifact: `artifacts/phase6nb-amzn-drv-test-source-closure-20260810-04/`
- Phase 6ND Image marker artifact: `artifacts/phase6nd-amzn-drv-test-image-marker-20260810-01/`
- Phase 6NP synthesis/evidence: `findings/phase-6np-ion-and-control-surface-closure.md`, `findings/phase-6np-evidence-index.md`
- Phase 6N read-only metadata: `adb/phase6n/PHASE6N-KERNEL-RO-20260810-01/`
- SELinux/file-context corpus: `artifacts/phase6c/phase6c-image-policy-extract-20260804-02/` and `...-05/`

