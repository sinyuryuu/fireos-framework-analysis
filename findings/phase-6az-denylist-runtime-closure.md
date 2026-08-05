# Phase 6AZ — KFT launcher-state path and PackageManager deny-list closure

Generated 2026-08-05. This phase combines the already-published KFT static
audit, the PS7331 resource provenance closure, and one explicit-serial
read-only device capture. It does not invoke the KFT service, send an OTA
broadcast, call a private Binder transaction, or mutate the device.

## Executive result

Two different Amazon mechanisms must be kept separate:

```text
ordinary user-0 shell mutation
  -> PackageManager protected-package callback
  -> Amazon deny-list membership
  -> system/privileged package + caller UID 2000
  -> rejection before enabled-state mutation

eligible KFT child-user lifecycle
  -> AmazonUserManagerService.onBootPhase(500)
  -> enableKftLauncherComponent(UserInfo)
  -> enable FreeTimeLauncherActivity
  -> setApplicationEnabledSetting(com.amazon.firelauncher, 2, 0, userId)
  -> setApplicationEnabledSetting(com.android.launcher3, 2, 0, userId)
```

The first path explains the observed ADB refusal. The second path confirms
that Amazon has a separate privileged KFT path capable of disabling Fire
Launcher, but it is not evidence that ordinary user-0 HOME resolution uses
that path. The KFT branch was not invoked on the device.

## Findings and confidence

### Confirmed — KFT contains a Fire Launcher disable call (static only)

`AmazonUserManagerService.BinderService.enableKftLauncherComponent(UserInfo)`
in the PS7331 `fosservices` VDEX disassembly (lines 54297–54325) constructs
the FreeTime launcher component, enables it, then calls
`setApplicationEnabledSetting` with integer state `2` for both
`com.amazon.firelauncher` and `com.android.launcher3`. Android 9 defines state
`2` as `COMPONENT_ENABLED_STATE_DISABLED` in the saved AOSP framework reference
(`PackageManager.java`, lines 640–646).

This is a static fact. The parser summary records
`device_contacted=false`, `binder_invoked=false`,
`dpm_or_profile_owner_invoked=false`, and
`package_or_settings_state_changed=false`.

### Confirmed — the KFT call is lifecycle- and user-gated (static only)

`tryEnableKftLauncherComponent(UserInfo)` (lines 54371–54414) performs
eligibility checks before the state mutation. `enableKftLauncher(UserInfo)`
(lines 54415–54478) is coupled to internal Device Policy/profile-owner
operations. `AmazonUserManagerService.onBootPhase(int)` (lines 55053–55105)
selects boot phase 500, upgrade state, and child users before invoking the KFT
path.

Therefore the existence of the call does not authorize replaying it through
ADB, and it does not establish a normal user-0 HOME workaround.

### Confirmed — PS7331 resource explicitly seeds Fire Launcher into the deny-list

The matched PS7331 system image has SHA-256
`da8a935484de24251e890fbf4e7dd9155567ebe158fc255d43684ea14c62b1e5`. A
read-only `debugfs dump` extracted `/system/framework/fireos-res/fireos-res.apk`.
Its resource table maps `0x7e05000a` to
`amazon.fireos:raw/package_manager_deny_list`, and the extracted JSON contains
`com.amazon.firelauncher` in `packages_deny_list`.

The corresponding static consumer is
`DenyListArcusHelper.processJSON()` (fosservices VDEX, around lines 97326–97348),
which opens resource `0x7e05000a`; the stored set is consumed by
`ControlProtectedPackagesCallback.shouldProtectPackage(int,String,Context)`
(lines 97034–97049).

### Confirmed — the protected gate has a caller-sensitive Amazon callback

`VendorProtectedPackagesCallback.callShouldProtectPackage` in the standard
services VDEX (lines 539225–539239) ORs registered vendor callbacks. The Amazon
`ControlProtectedPackagesCallback` checks the system/privileged application
flag, membership in `PackageManagerDenyList:DenyListKeyPackages`, and caller
UID `2000`. The callback is registered by
`artifacts/amazon-services/amazonpackagemanager_fosinit.xml:22`.

The previously sealed component-disable tests observed the rejection before
package or component state changed. Combined with the exact PS7331 resource
membership, this gives a closed static explanation for Fire Launcher's
ordinary shell protection.

### Strong evidence — current device state is consistent with the closure

The explicit-serial read-only capture `PHASE6AZ-RO-20260805-04` reports:

* fingerprint `Amazon/trona/trona:9/PS7331.4463N/0031575863040:user/amz-p,release-keys`;
* model `KFTRWI`, API 28, security patch `2024-08-01`, verified boot `green`;
* HOME resolver `com.amazon.firelauncher/.Launcher`, effective priority 50;
* Fire Launcher at `/system/priv-app/com.amazon.firelauncher`, with SYSTEM and
  PRIVILEGED flags and user-0 enabled state 0 (default);
* SELinux enforcing and shell UID 2000;
* no visible shell service handle for `amazonpackagemanager`,
  `amazonusermanagerservice`, `amazonactivitymanager`, or
  `amazonwindowmanager`.

The public redacted form is under
`artifacts/phase6az/public-summary-20260805-02/`; the full serial capture is
kept locally under `adb/phase6az/PHASE6AZ-RO-20260805-04/` and is not
published because it contains broad settings and activity dumps.

The capture is not a pristine app inventory: the existing research packages
`org.fireosresearch.phase4.alias` and
`org.fireosresearch.phase4.redirect` are present, and the latter is listed in
`enabled_accessibility_services`. No package or setting was changed by this
phase.

### Disproved as the active Fire OS HOME selector — `tb_custom_launcher`

The read-only capture returned `tb_custom_launcher=com.teslacoilsw.launcher`,
but `dumpsys package com.teslacoilsw.launcher` returned `Unable to find
package`. A repository-wide static search of the preserved decompiled,
firmware, and framework artifacts found no reader or writer that uses this key
to choose HOME; the existing Phase 3C inventory likewise records no observed
HOME-specific reader/writer.

This supports classifying the key as stale legacy/tool state rather than an
active Fire OS HOME control. It does not justify deleting or changing the key;
no mutation was attempted.

### Not established

This phase does not prove that the current persisted
`/data/system/PackageManagerDenyList` contents have not been replaced by an
Arcus refresh. Shell can observe its metadata and ACL but cannot read its
contents under enforcing SELinux. It also does not prove that KFT is reachable
for any particular non-child user or that the KFT path would be safe to invoke.

## Safety record

No `pm disable-user`, `pm hide`, `pm suspend`, `pm uninstall`, `pm clear`,
`settings put/delete`, `device_config put/delete`, overlay mutation, reboot,
private Binder transaction, protected broadcast replay, OTA/recovery command,
root operation, partition write, or SELinux change was performed.

## Reproduction

Host-only resource closure:

```sh
python3 tools/scripts/audit_phase6ap_denylist_resource.py --dry-run
python3 tools/scripts/audit_phase6ap_denylist_resource.py \
  --image firmware/extracted/PS7331/system.img \
  --output artifacts/phase6ap/denylist-resource-closure-20260805-01
```

Read-only device capture (requires an explicitly selected serial):

```sh
tools/scripts/capture_phase6az_readonly.sh \
  --serial DEVICE_SERIAL \
  --output adb/phase6az/PHASE6AZ-RO-YYYYMMDD-NN
python3 tools/scripts/build_phase6az_public_summary.py \
  --input adb/phase6az/PHASE6AZ-RO-YYYYMMDD-NN \
  --output artifacts/phase6az/public-summary-YYYYMMDD-NN
```

The capture script contains read-only commands only and refuses to overwrite
an output directory.
