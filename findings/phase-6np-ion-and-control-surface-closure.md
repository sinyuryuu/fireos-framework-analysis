# Phase 6NP — PS7331 ION／driver control-surface closure

## Scope

This phase is a host-only, defensive review of the PS7331 source, extracted
SELinux policy and previously captured device metadata. It does not open a
device node, issue an ioctl, compile or execute an exploit, modify the device,
or change Fire Launcher state.

The review was selected because the earlier Phase 5 capture showed a permissive
`/dev/ion` Unix mode and the extracted policy appeared to allow `shell` access.
The question is whether that observation forms a complete ordinary-caller
path to a kernel primitive, PackageManager, ActivityTaskManager or HOME state.

## Executive result

| Finding | Status | Evidence-based conclusion |
|---|---|---|
| PS7331 policy labels `/dev/ion` as `ion_device` | Confirmed | Both platform and vendor file-context inputs map `/dev/ion` to `ion_device`. |
| `shell`, `untrusted_app` and `system_app` inherit an ION chr-file allow | Confirmed for the extracted policy | `base_typeattr_43` is used for `ioctl/read/write/getattr/lock/append/map/open`; this is host-side policy evidence, not a live probe. |
| ION ioctl surface exists in the selected MT8183 4.4 source | Confirmed | The driver dispatches alloc/free/map/share/import/sync/custom requests and registers unlocked/compat ioctl handlers. |
| Ordinary APK/JAR directly calls ION | Strong evidence against | The bounded scan covered 307 APK/JAR inputs and found no ION token or `libion` caller. This is not an absolute statement about binaries outside the captured corpus. |
| Shell has a demonstrated live ION caller or memory-safety primitive | Not established | Historical node metadata and SELinux allow are not proof of a successful open/ioctl or of a vulnerability. No node was opened. |
| ION influences HOME, PMS or ATMS | Disproved within the audited source/data-flow scope | No driver-to-PackageManager, ActivityManager, HOME resolver or launcher-state writer was found. |
| `amzn_drv_test` is built into the PS7331 image | Strong negative | The final kernel config says `# CONFIG_AMZN_DRV_TEST is not set`; image marker audit is zero. Loadable-module packaging remains an explicit unknown. |
| `tmem0` is a PS7331 runtime entry point | Unknown | Source-only material was not matched to config, module, file-context, policy and runtime-node evidence. |

## ION policy and labeling

The extracted PS7331 policy contains:

```text
(allow base_typeattr_43 ion_device
    (chr_file (ioctl read write getattr lock append map open)))
(auditallow appdomain ion_device (chr_file (write append)))
```

The first rule is an allow rule. The second is an audit rule and must not be
misread as a denial. `base_typeattr_43` is tied to the platform `appdomain`
definition and, in the extracted policy, covers `shell`, `system_app` and
`untrusted_app` while excluding `isolated_app`. No `ion_device`-specific
`neverallow` intersecting that allow was found in the audited platform/vendor
CIL inputs. `vendor_app` is not in that platform appdomain definition and has
no corresponding ION allow in the audited policy.

The relevant inputs are:

- `artifacts/phase6c/phase6c-image-policy-extract-20260804-02/system/etc/selinux/plat_sepolicy.cil:639,4464-4465,1228-1229,16950-16951`
- `artifacts/phase6c/phase6c-image-policy-extract-20260804-02/system/etc/selinux/plat_file_contexts:226`
- `artifacts/phase6c/phase6c-image-policy-extract-20260804-02/system/etc/selinux/vendor_file_contexts:198`
- `artifacts/phase6c/phase6c-image-policy-extract-20260804-02/system/etc/selinux/vendor_sepolicy.cil`

The policy hashes are recorded in
`findings/phase-6np-evidence-index.md`. The precompiled policy has a hash but
does not provide text line locations, so this report does not claim that the
currently booted policy was independently decoded from the device.

## Live metadata-only corroboration

Capture `adb/phase6np/PHASE6NP-ION-METADATA-20260810-01/` verified, without
opening the nodes, that the current device exposes `/dev/ion` as mode `0666`
with owner `system:graphics` and label `ion_device`. The same capture reports
SELinux `Enforcing` and the executing context `u:r:shell:s0`. It also records
the neighboring CMDQ and GED metadata. This is stronger than relying only on
an old device snapshot for node existence, but it remains metadata evidence:
no ION operation was issued and no memory or privilege effect was tested.

## ION source and caller boundary

The build-selected source contains the standard ION UAPI and MTK custom path:

- `platform/kernel/mediatek/mt8183/4.4/drivers/staging/android/ion/uapi/ion.h`
- `platform/kernel/mediatek/mt8183/4.4/drivers/staging/android/ion/ion.c`
- `platform/kernel/mediatek/mt8183/4.4/drivers/staging/android/ion/mtk/ion_drv.c`
- `platform/kernel/mediatek/mt8183/4.4/drivers/staging/android/ion/mtk/ion_drv.h`
- `platform/kernel/mediatek/mt8183/4.4/drivers/staging/android/ion/compat_ion.c`

`ion.c` contains the userspace dispatch and `unlocked_ioctl`/
`compat_ioctl` registration. The source supports allocation, release, map,
share, import, sync and architecture-specific custom requests. Existence of
these operations is capability evidence only; it is not evidence of a bug or
of arbitrary kernel memory access.

The bounded native scan found ION symbols in system/vendor graphics, camera,
codec and media libraries, including gralloc, hwcomposer, camera memory and
VPU helpers. Their init definitions run as managed system services such as
`system`, `cameraserver`, `media` or `mediacodec`. No APK/JAR in the 307-input
scan directly referenced `/dev/ion`, `ION_IOC_*`, `ion_open`, `ion_alloc`,
`ion_custom_ioctl` or `libion*.so`.

This leaves an important distinction:

```text
policy allow / historical node metadata
        != successful live caller
        != memory-safety defect
        != privilege escalation
        != HOME replacement
```

## Adjacent driver surfaces

| Surface | Current status | Reason |
|---|---|---|
| CMDQ v3 | Bounded negative for the HOME route | The selected dispatcher was reviewed; no direct HOME/PMS edge or ordinary-app proof was found. Device node access was not expanded into ioctl testing. |
| GED | Bounded negative for the HOME route | Existing Phase 6BQ work observed query-only telemetry; no launcher or PackageManager sink. |
| `amzn_drv_test` | Strong negative for built-in image; module status unknown | Source has a `/proc/amzn_drvs` concept, but config and image markers exclude the built-in driver. No runtime proc write was attempted. |
| `tmem0` | Unknown | Source material was not closed through config, module packaging, file context, SELinux and runtime existence. No proc/sysfs/debugfs access was attempted. |
| ION debugfs | Not a tested route | The audited policy did not establish ordinary read/write/ioctl access to the debugfs files. |

## Module and overlay packaging closure

The follow-up host-only packaging audit closes the remaining ambiguity for the
two source-only candidates:

- `amzn_drv_test` is a `tristate` source target, but the PS7331 `trona_defconfig`
  does not enable it and the final `kernel.config:3584` says
  `# CONFIG_AMZN_DRV_TEST is not set`.
- `tmem0` has a module-capable source path, but its build configuration is
  tied to engineering/trusted-memory options that are not enabled in the
  selected PS7331 config. No product `.ko`, `modules.dep`, `modules.load`,
  `vendor_dlkm`, or `odm` packaging evidence was found.
- `CONFIG_MODULES=y` at `kernel.config:250` is only generic module support;
  it does not establish that either candidate was delivered as a loadable
  module.
- `CONFIG_OF_OVERLAY`, `CONFIG_OVERLAY_FS` and target ODM copy-out are not
  enabled in the inspected config. The extracted PS7331 image has no matching
  `vendor_dlkm` or `odm` overlay payload.

This is a **Strong negative** for a delivered `amzn_drv_test` module and a
**bounded Unknown** for `tmem0` runtime existence. The source remains useful
for defensive comparison, but no further device probing is justified without
new image provenance.

## Relation to the launcher objective

The IPC/OTA and launcher reviews in this continuation found no new ordinary
caller that writes User-0 HOME, preferred activity, or Fire Launcher package
state. The strongest currently measured rootless behavior remains a
user-consented Accessibility/PendingIntent foreground redirect. It is a
foreground fallback, not a formal HOME replacement; the resolver still
returns `com.amazon.firelauncher/.Launcher`.

The ION surface does not change that conclusion. No audited ION caller or
driver path reaches PackageManager, ActivityTaskManager, SystemUI HOME logic,
or an Amazon launcher-state writer.

## Safety boundary and rejected tests

The following were intentionally not performed:

- opening `/dev/ion` or any other device node;
- sending `ION_IOC_*`, CMDQ, procfs, sysfs or debugfs operations;
- crafting an ION/custom ioctl payload;
- compiling or executing a kernel exploit or privilege-escalation payload;
- invoking unknown Binder transactions or private services;
- disabling, hiding, suspending, force-stopping or clearing Fire Launcher;
- OTA/recovery/bootloader/partition writes.

These are marked **因風險拒絕測試**, not failures and not evidence that a
vulnerability exists.

## Stop decision and next research boundary

The host-only packaging closure is complete. The driver line should stop at
this boundary unless new provenance identifies a delivered module, a trusted
caller, or a direct framework sink. No device-node operation is justified by
the present evidence.

The remaining launcher work is separate: a formal User-0 HOME replacement is
still unconfirmed, while the only measured practical fallback is the
user-consented Accessibility/PendingIntent foreground redirect. Any future
measurement of that fallback must retain visible manual consent and the
existing rollback guard.
