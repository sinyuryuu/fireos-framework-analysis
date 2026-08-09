# Phase 6KV — PMS/HOME caller-to-sink closure

Date: 2026-08-10
Device target: Fire HD 10 (KFTRWI/trona), Fire OS 7.3.3.1 / PS7331
Mode: **host-only, read-only**

## Executive result

The preserved PS7331 `fosservices` and `services` VDEX disassembly contains 25
exact invoke sites that touch the bounded package-state or preferred-activity
sinks indexed by this phase. The index finds:

- the known KFT launcher-state writer, whose three calls are in
  `AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)`
  and use the supplied `UserInfo.id`;
- fixed-scope OOBE, Gemini, Espresso and ProductPolicy component/package
  writers; and
- the standard shell, DevicePolicy and PackageManager framework paths.

It does **not** find a new Amazon `fosservices` implementation that calls
`setHomeActivity`, `replacePreferredActivity`,
`addPersistentPreferredActivity`, or a HOME-specific User-0 restoration API.
This is a static caller inventory, not proof that any row is reachable from
shell or that it changes User 0.

Finding status: **Strong evidence — no new User-0 HOME writer in the reviewed
artifacts.** The existing physical reachability evidence remains authoritative:
the candidate private Amazon services were not obtainable by shell and no
unknown Binder transaction was sent. A fresh read-only repeat on
`2026-08-09 19:12:43` produced the same result and left the Fire package and
HOME resolver unchanged.

## Evidence and reproducibility

The parser is:

```text
tools/scripts/audit_phase6kv_pms_home_callers.py
```

The source provenance/scope checker is:

```text
tools/scripts/audit_phase6kv_source_scope.py
```

It generated `artifacts/phase6kv/source-scope-20260810-01/manifest.json` and
`output/tables/phase6kv-source-scope.csv` without unpacking, building or
executing the source tree.

It reads only these preserved text artifacts:

| Evidence ID | Input | SHA-256 |
|---|---|---|
| `6KV-DIS-001` | `decompiled/baksmali/vdexExtractor/fosservices/disassembly.log` | `ecbe62fe8eb8bd575da8b2a73a155875df937073ccc2faa020ca592c0515151c` |
| `6KV-DIS-002` | `decompiled/baksmali/vdexExtractor/services/disassembly.log` | `373a51150fcb079da026b20e71d44380bc3d86e52be88c63ebd39cfd58a6ba53` |

Re-run from the repository root:

```sh
python3 tools/scripts/audit_phase6kv_pms_home_callers.py --root .
```

The run produced 25 rows. The canonical table and a hash manifest are:

- `output/tables/phase6kv-pms-home-callers.csv`
- `output/tables/phase6kv-source-scope.csv`
- `artifacts/phase6kv/pms-home-caller-closure-20260810-01/manifest.json`

The canonical table hash from this run is:

```text
c7e608c6e6c16502378c6093e8e979cd4d644c3c89d3b3bc3a01ef97295ff206
```

The parser deliberately labels every row `static_invoke_site_only`. It does
not infer caller UID, Binder reachability, user scope, or runtime execution
from an instruction alone.

The repeat device capture is:

```text
adb/phase6ep/PHASE6EP-AMAZON-WRITER-REACHABILITY-20260809-191243/
```

Its `result.json` SHA-256 is
`465be89b25ec6b731fd8d1f3de57636a8265a9a4ce5fdb61c69e3ba0bd73cd59`.

## Static call-site results

### Amazon `fosservices` rows

| Class / method | Sink | Static classification | Location |
|---|---|---|---|
| `AppAdapterHandler.goToRegistration()` | `PackageManager.setComponentEnabledSetting` | OOBE fixed component writer | `fosservices/disassembly.log:26056` |
| `GeminiHandler.disableGeminiIfRequired()` | `PackageManager.setApplicationEnabledSetting` | fixed Gemini package writer | `fosservices/disassembly.log:30354` |
| `AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)` | `AmazonPackageManager.setComponentEnabledSetting` | child-user scoped launcher-state writer | `fosservices/disassembly.log:54310` |
| same | `AmazonPackageManager.setApplicationEnabledSetting` | child-user scoped launcher-state writer | `fosservices/disassembly.log:54318,54324` |
| `EspressoShotCallback.disableBootCompleteReceivers()` / `reEnableBootCompleteReceivers()` | `PackageManager.setComponentEnabledSetting` | BOOT receiver lifecycle writer | `fosservices/disassembly.log:191881,192065` |
| `EnableDisableComponentAction.enableDisableComponent(String,IZ)` | Amazon package/component setters | ProductPolicy fixed-policy writer | `fosservices/disassembly.log:293712-293738` |

The KFT method has the Fire and Launcher3 literals and a Tahoe launcher
component. The immediate argument is `UserInfo.id`; the source report for the
same method and the child-user runtime evidence must be read together. The
literal alone does not prove a User-0 invocation.

### Standard `services` rows

The 14 `services` rows are standard framework or system-service callers:

- `PackageManagerShellCommand.runSetEnabledSetting()` — shell front end to
  package/component state mutation (`services/disassembly.log:500744-500765`).
- `PackageManagerService.setHomeActivity()` →
  `PackageManagerService.replacePreferredActivity()`
  (`services/disassembly.log:966912-966955`).
- `DevicePolicyManagerService.enableIfNecessary()` and `enableSystemApp()` —
  owner/policy path, not ordinary shell evidence
  (`services/disassembly.log:832035,840319`).
- `PackageManagerService` internal preferred-state cleanup and reset callers —
  `clearPackagePreferredActivities` at the indexed rows.
- Bluetooth, InputMethod, AMS development/system-ready and WebView
  `SystemImpl` package/component callers, none of which is a new Fire HOME
  writer in this inventory.

The presence of `PackageManagerShellCommand` and the PMS method does not imply
that the shell can bypass the PMS gate. Earlier Phase 2/6 evidence records the
opposite for Fire Launcher state mutation, and the `set-home-activity` result
already demonstrates a preferred record can persist while formal HOME remains
Fire.

## What this closes and what it does not

### Closed within this static scope

1. **No new Amazon HOME setter:** no Amazon `fosservices` invoke site for the
   four preferred/HOME setter names searched by this phase.
2. **KFT remains the only launcher-specific Amazon state writer found:** its
   scope is represented by a supplied `UserInfo`, not an unconditional User-0
   write in the observed method.
3. **ProductPolicy is not a generic HOME switch:** its call sites are fixed
   policy actions; the existing PS7331 policy input review did not contain
   `com.amazon.firelauncher`.
4. **A service name is not an IPC route:** the physical Phase 6EP/6KU probes
   recorded private service names but no shell Binder handle and sent no
   transaction.

### Not established by this phase

- a complete proof that every boot-time Amazon callback has been recovered;
- runtime invocation of each static call site;
- a proof that Fire's priority-50 result is caused by a private callback rather
  than the AOSP-shaped resolver and package metadata;
- a permission vulnerability or a confused deputy;
- a viable way to disable Fire Launcher or replace User-0 HOME.

Those claims remain **unconfirmed** unless supported by the corresponding
device evidence or a more complete framework artifact.

## GPL source scope cross-check

The PS7331 source package is useful for kernel/vendor provenance, but it is not
a source drop for the complete Fire framework:

| Evidence ID | Artifact | SHA-256 / result |
|---|---|---|
| `6KV-SRC-001` | `firmware/original/Fire_HD10-7.3.3.1-20250617.tar.bz2` | `02ffafddb97999ebcc4419dda28cab9ea6ddacf7123b1301a073a3809c762aea` |
| `6KV-SRC-002` | extracted `platform.tar` | `69c62d65a387e22b39678df8054e6cae12b4d95b8c5d9bf21ad53811491a7fdd` |
| `6KV-SRC-003` | extracted `fireos.tar` | `bb7030296545dd45edcfec47d3e742043e7813852844f4b0fbbe8d223899b369` |
| `6KV-SRC-004` | `platform/kernel/mediatek/mt8183/4.4/arch/arm64/configs/trona_defconfig` | `09ca8dfc3b3b5e139482e3dd9976dae79547077fb750a4cbc778814f85ecaaac` |

Observed source scope:

- MT8183 4.4 kernel and `trona_defconfig` are present;
- MediaTek `drivers/misc/mediatek`, input, power, USB and char trees are
  present;
- Amazon custom kernel drivers are present under
  `platform/device/amazon/kernel/driver/`, including `amzn_idme.c`,
  `amzn_logger.c`, `amzn_keycombo.c`, sign-of-life and driver-test sources;
- `platform/system/core/` exists, but the exact
  `platform/system/core/init/selinux.cpp` path is absent from the extracted
  source tree;
- no `rootable_*_sepolicy.cil` source file was found in the GPL source tree;
- no matching Amazon userspace framework-service implementation was found in
  the GPL source tree. Firmware APK/JAR artifacts remain the authoritative
  input for those services.

This is a **source-scope finding**, not evidence that an absent file is dead
code or that a rootable policy is loadable.

## Safety boundary

No device command, Binder transaction, APK, native binary, ioctl, OTA,
recovery, reboot, package mutation, settings write, Fire Launcher mutation or
unknown service call was used by this phase. The user's device unlock PIN was
not used or stored.

## Next smallest useful analysis

The highest-value low-risk continuation is a method-level comparison of the
PMS resolver and its AOSP Android 9 counterpart, using the already extracted
`services` VDEX and preserved AOSP references. It should answer whether the
Fire result can be reproduced from candidate priority/match/metadata without
inventing a private Amazon HOME writer. A new Binder transaction or a Fire
package-state mutation is not justified by this static inventory.
